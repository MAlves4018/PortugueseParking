from unittest.mock import MagicMock
from django.test import TestCase
from django.utils import timezone
from parking.models import Gate
from contracts.services import TicketService


class EnterWithSeasonTicketTests(TestCase):
    """
    Unit tests for UC2: entry with a season ticket.

    Uses mocks for:
    - vehicle repo
    - contract repo
    - movement repo
    - gate repo
    """

    def setUp(self):
        self.mock_pricing = MagicMock()
        self.mock_payment = MagicMock()

        self.mock_vehicle_repo = MagicMock()
        self.mock_contract_repo = MagicMock()
        self.mock_movement_repo = MagicMock()
        self.mock_gate_repo = MagicMock()
        self.mock_gate_repo.model = Gate


        self.service = TicketService(
            pricing_service=self.mock_pricing,
            payment_service=self.mock_payment,
            vehicle_repo=self.mock_vehicle_repo,
            contract_repo=self.mock_contract_repo,
            movement_repo=self.mock_movement_repo,
            gate_repo=self.mock_gate_repo,
        )

        self.plate = "AA-11-BB"
        self.gate_id = 5

        self.now = timezone.now()

    # ---------------------------------------------------------
    # HAPPY PATH
    # ---------------------------------------------------------
    def test_entry_success(self):
        """UC2: Should open gate when vehicle + contract + movement OK."""

        vehicle_mock = MagicMock()
        self.mock_vehicle_repo.get.return_value = vehicle_mock

        contract_mock = MagicMock()
        self.mock_contract_repo.filter.return_value.exists.return_value = True
        self.mock_contract_repo.filter.return_value.select_for_update.return_value.first.return_value = contract_mock

        # No open movements
        self.mock_movement_repo.filter.return_value.exists.return_value = False

        movement_instance = MagicMock(pk=999)
        self.mock_movement_repo.create.return_value = movement_instance

        self.mock_gate_repo.get.return_value = MagicMock()

        result = self.service.enter_with_season_ticket(self.plate, self.gate_id)

        self.assertTrue(result["success"])
        self.assertTrue(result["open_gate"])
        self.assertEqual(result["movement_id"], 999)

    # ---------------------------------------------------------
    # NEGATIVE CASES
    # ---------------------------------------------------------

    def test_vehicle_not_found(self):
        """UC2: Should fail when vehicle does not exist."""

        self.mock_vehicle_repo.get.side_effect = self.mock_vehicle_repo.model.DoesNotExist

        result = self.service.enter_with_season_ticket(self.plate, self.gate_id)

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])

    def test_no_active_ticket(self):
        """UC2: Should fail when no valid contract exists."""

        self.mock_vehicle_repo.get.return_value = MagicMock()

        # No contracts returned
        self.mock_contract_repo.filter.return_value.exists.return_value = False

        result = self.service.enter_with_season_ticket(self.plate, self.gate_id)

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])

    def test_ticket_already_in_use(self):
        """UC2: Should reject if an open movement already exists."""

        self.mock_vehicle_repo.get.return_value = MagicMock()

        # Contract exists
        contract_qs = MagicMock()
        contract_qs.exists.return_value = True
        contract_qs.select_for_update.return_value.first.return_value = MagicMock()
        self.mock_contract_repo.filter.return_value = contract_qs

        # Movement exists (open)
        self.mock_movement_repo.filter.return_value.exists.return_value = True

        result = self.service.enter_with_season_ticket(self.plate, self.gate_id)

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])

    def test_gate_not_found(self):
        """UC2: Should fail if gate does not exist."""

        self.mock_vehicle_repo.get.return_value = MagicMock()

        # Contract exists
        contract_qs = MagicMock()
        contract_qs.exists.return_value = True
        contract_qs.select_for_update.return_value.first.return_value = MagicMock()
        self.mock_contract_repo.filter.return_value = contract_qs

        # No open movement
        self.mock_movement_repo.filter.return_value.exists.return_value = False

        # Gate fails
        self.mock_gate_repo.get.side_effect = Gate.DoesNotExist

        result = self.service.enter_with_season_ticket(self.plate, self.gate_id)

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
