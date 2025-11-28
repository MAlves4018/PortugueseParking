from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class OccasionalTicketViewsTests(TestCase):
    """
    UI-level tests para os casos de uso com bilhetes ocasionais (UC3).

    - Entrada ocasional
    - Saída ocasional
    - Pagamento no cash device (calculate / pay)
    """

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="cashier",
            password="secret",
            email="cashier@example.com",
        )
        self.client.login(username="cashier", password="secret")

    def test_occasional_entry_get_renders_page(self):
        """
        Smoke test: a página de entrada ocasional deve carregar.
        """
        url = reverse("contracts:gate_occasional_entry")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Texto genérico do header, para não depender do tipo de travessão.
        self.assertContains(response, "Occasional", status_code=200)

    def test_occasional_exit_get_renders_page(self):
        """
        Smoke test: a página de saída ocasional deve carregar.
        """
        url = reverse("contracts:gate_occasional_exit")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Occasional", status_code=200)

    @patch("contracts.views._build_ticket_service")
    def test_cash_device_calculate_uses_service_and_shows_amount(
        self,
        mock_build_service,
    ):
        """
        UC3 – Cash device, ação "Calculate price".

        A view deve:
        - construir o serviço via _build_ticket_service()
        - chamar service.get_occasional_pricing(plate)
        - mostrar o montante a pagar.
        """
        fake_pricing = {
            "success": True,
            "duration_minutes": 90,
            "amount": 5.50,
            "reason": "OK",
        }

        mock_service = MagicMock()
        mock_service.get_occasional_pricing.return_value = fake_pricing
        mock_build_service.return_value = mock_service

        url = reverse("contracts:occasional_cash_device")
        data = {
            "license_plate": "OC-11-22",
            "action": "calculate",
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)

        # O serviço deve ter sido chamado com a matrícula correta
        mock_service.get_occasional_pricing.assert_called_once_with("OC-11-22")

        # O template mostra algo como "Amount due: X €"
        self.assertContains(response, "Amount due")

    @patch("contracts.views._build_ticket_service")
    def test_cash_device_pay_uses_service_and_shows_success(
        self,
        mock_build_service,
    ):
        """
        UC3 – Cash device, ação "Pay now".

        A view deve:
        - construir o serviço via _build_ticket_service()
        - chamar service.pay_occasional_ticket(plate)
        - mostrar uma mensagem de sucesso e o valor pago.
        """
        fake_payment_result = {
            "success": True,
            "reason": "Payment successful.",
            "amount": 7.25,
            "deadline": "2025-01-01 12:00",
        }

        mock_service = MagicMock()
        mock_service.pay_occasional_ticket.return_value = fake_payment_result
        mock_build_service.return_value = mock_service

        url = reverse("contracts:occasional_cash_device")
        data = {
            "license_plate": "OC-11-22",
            "action": "pay",
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)

        mock_service.pay_occasional_ticket.assert_called_once_with("OC-11-22")

        # O template mostra "Paid: <amount> €" e a razão
        self.assertContains(response, "Paid:")
        self.assertContains(response, "Payment successful.")
