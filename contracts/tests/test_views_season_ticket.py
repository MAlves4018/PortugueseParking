from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SeasonTicketViewsTests(TestCase):
    """
    UI-level tests para os casos de uso com season ticket.

    - UC1: compra de season ticket (view 'season_ticket_new')
    - UC2: gate entry / gate exit com season ticket
    """

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="secret",
            email="test@example.com",
        )
        # Autenticar o utilizador para passar o @login_required nas views.
        self.client.login(username="testuser", password="secret")

    @patch("contracts.views._build_ticket_service")
    @patch("contracts.views._get_available_slots_for")
    @patch("contracts.views.Vehicle")
    def test_season_ticket_new_post_uses_service_and_redirects(
        self,
        mock_vehicle_cls,
        mock_get_slots,
        mock_build_service,
    ):
        """
        UC1 – Purchase season ticket.

        A view deve:
        - construir o serviço via _build_ticket_service()
        - chamar service.purchase_season_ticket(...)
        - redirecionar para a lista de season tickets em caso de sucesso.
        """
        # --- Arrange serviço ---
        mock_service = MagicMock()
        mock_service.purchase_season_ticket.return_value = {
            "success": True,
            "reason": "Season ticket created successfully.",
        }
        mock_build_service.return_value = mock_service

        # --- Arrange Vehicle + slots (mock do modelo = isolar UI) ---
        fake_vehicle = MagicMock()
        fake_vehicle.license_plate = "AA-00-BB"

        # qualquer get(...) devolve o mesmo veículo falso
        mock_vehicle_cls.objects.get.return_value = fake_vehicle

        # _get_available_slots_for devolve um slot com id "10"
        fake_slot = MagicMock()
        fake_slot.id = "10"
        mock_get_slots.return_value = [fake_slot]

        url = reverse("contracts:season_ticket_new")

        # Campos alinhados com os nomes esperados pela view:
        # vehicle_id, slot_id, valid_from, valid_to, action="confirm"
        form_data = {
            "vehicle_id": "1",
            "slot_id": "10",
            "valid_from": "2025-01-01 08:00",
            "valid_to": "2025-01-31 20:00",
            "action": "confirm",
        }

        # --- Act ---
        response = self.client.post(url, data=form_data)

        # --- Assert ---
        # Deve ter chamado o builder para obter o serviço
        mock_build_service.assert_called_once()

        # Deve ter chamado o método de negócio para comprar o season ticket
        mock_service.purchase_season_ticket.assert_called_once()

        # Em caso de sucesso a view faz redirect para season_ticket_list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("contracts:season_ticket_list"))

    @patch("contracts.views._build_ticket_service")
    def test_gate_entry_post_calls_service_and_shows_message(
        self,
        mock_build_service,
    ):
        """
        UC2 – Gate entry com season ticket (happy path).

        A view deve:
        - construir o serviço via _build_ticket_service()
        - chamar service.enter_with_season_ticket(...)
        - mostrar a mensagem devolvida em 'reason'.
        """
        mock_service = MagicMock()
        mock_service.enter_with_season_ticket.return_value = {
            "success": True,
            "open_gate": True,
            "reason": "Gate opened for vehicle.",
        }
        mock_build_service.return_value = mock_service

        url = reverse("contracts:gate_entry")
        data = {
            "license_plate": "11-AA-11",
            "gate_id": "123e4567-e89b-12d3-a456-426614174000",
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)

        # O service deve ter sido chamado com a matrícula em upper-case e o gate_id
        mock_service.enter_with_season_ticket.assert_called_once_with(
            "11-AA-11",
            "123e4567-e89b-12d3-a456-426614174000",
        )

        # O template deve apresentar a mensagem
        self.assertContains(response, "Gate opened for vehicle.")

    @patch("contracts.views._build_ticket_service")
    def test_gate_exit_post_calls_service_and_shows_message(
        self,
        mock_build_service,
    ):
        """
        UC2 – Gate exit com season ticket.

        A view deve:
        - construir o serviço via _build_ticket_service()
        - chamar service.exit_with_season_ticket(...)
        - mostrar a mensagem devolvida em 'reason'.
        """
        mock_service = MagicMock()
        mock_service.exit_with_season_ticket.return_value = {
            "success": True,
            "open_gate": True,
            "reason": "Exit registered, gate opened.",
        }
        mock_build_service.return_value = mock_service

        url = reverse("contracts:gate_exit")
        data = {
            "license_plate": "11-AA-11",
            "gate_id": "123e4567-e89b-12d3-a456-426614174000",
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)

        mock_service.exit_with_season_ticket.assert_called_once_with(
            "11-AA-11",
            "123e4567-e89b-12d3-a456-426614174000",
        )

        self.assertContains(response, "Exit registered, gate opened.")
