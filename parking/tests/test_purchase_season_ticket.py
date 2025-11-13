from unittest.mock import MagicMock
from django.test import TestCase
from django.utils import timezone

from contracts.services import TicketService
from contracts.models import RegularContract
from vehicles.models import Vehicle
from parking.models import ParkingSlot


class PurchaseSeasonTicketTests(TestCase):
    """
    Unit tests for UC1: purchase_season_ticket.

    All persistence and collaborators are mocked.
    The goal is to test ONLY the business logic inside TicketService.
    """

    def setUp(self):
        # Mock dependencies
        self.mock_pricing = MagicMock()
        self.mock_payment = MagicMock()

        # Mock repositories
        self.mock_slot_repo = MagicMock()
        self.mock_vehicle_repo = MagicMock()
        self.mock_contract_repo = MagicMock()

        # Create the service under test
        self.service = TicketService(
            pricing_service=self.mock_pricing,
            payment_service=self.mock_payment,
            slot_repo=self.mock_slot_repo,
            vehicle_repo=self.mock_vehicle_repo,
            contract_repo=self.mock_contract_repo,
        )

        # Common test data
        self.customer_id = 1
        self.vehicle_plate = "AA-00-AA"
        self.slot_id = 10
        self.valid_from = timezone.now()
        self.valid_to = self.valid_from + timezone.timedelta(days=30)

    # ---------------------------------------------------------
    # HAPPY PATH
    # ---------------------------------------------------------
    def test_purchase_season_ticket_success(self):
        """UC1: Should create a contract when everything is valid."""

        # Prepare mocks
        vehicle_mock = MagicMock()
        vehicle_mock.owner_id = self.customer_id
        vehicle_mock.owner = MagicMock()

        slot_mock = MagicMock()

        self.mock_vehicle_repo.select_for_update().get.return_value = vehicle_mock
        self.mock_slot_repo.select_for_update().get.return_value = slot_mock

        # No overlapping contracts
        self.mock_contract_repo.filter().exists.return_value = False

        # Pricing returns 99.99
        self.mock_pricing.get_season_price.return_value = 99.99

        # Payment succeeds
        self.mock_payment.process_payment.return_value = True

        # Contract creation mock
        created_contract = MagicMock(pk=123)
        self.mock_contract_repo.create.return_value = created_contract

        # Execute
        result = self.service.purchase_season_ticket(
            customer_id=self.customer_id,
            vehicle_plate=self.vehicle_plate,
            slot_id=self.slot_id,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
        )

        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["contract_id"], 123)

        # Ensure correct methods were called
        self.mock_contract_repo.create.assert_called_once()

    # ---------------------------------------------------------
    # NEGATIVE CASES
    # ---------------------------------------------------------
    def test_slot_already_reserved(self):
        """UC1: Should reject when slot has an overlapping contract."""

        self.mock_vehicle_repo.select_for_update().get.return_value = MagicMock(owner_id=self.customer_id)
        self.mock_slot_repo.select_for_update().get.return_value = MagicMock()

        # Force overlap
        self.mock_contract_repo.filter().exists.return_value = True

        result = self.service.purchase_season_ticket(
            self.customer_id, self.vehicle_plate, self.slot_id, self.valid_from, self.valid_to
        )

        self.assertFalse(result["success"])
        self.assertIn("Slot already reserved", result["reason"])

    def test_payment_failed(self):
        """UC1: Should fail when payment is rejected."""

        self.mock_vehicle_repo.select_for_update().get.return_value = MagicMock(owner_id=self.customer_id)
        self.mock_slot_repo.select_for_update().get.return_value = MagicMock()
        self.mock_contract_repo.filter().exists.return_value = False

        # Price OK
        self.mock_pricing.get_season_price.return_value = 50

        # Payment fails
        self.mock_payment.process_payment.return_value = False

        result = self.service.purchase_season_ticket(
            self.customer_id, self.vehicle_plate, self.slot_id, self.valid_from, self.valid_to
        )

        self.assertFalse(result["success"])
        self.assertIn("Payment failed", result["reason"])

    def test_vehicle_not_found(self):
        """UC1: Should return error if vehicle does not exist."""

        self.mock_vehicle_repo.select_for_update().get.side_effect = self.mock_vehicle_repo.model.DoesNotExist

        result = self.service.purchase_season_ticket(
            self.customer_id, self.vehicle_plate, self.slot_id, self.valid_from, self.valid_to
        )

        self.assertFalse(result["success"])

    def test_slot_not_found(self):
        """UC1: Should fail if slot is missing."""

        # First vehicle is OK
        self.mock_vehicle_repo.select_for_update().get.return_value = MagicMock(owner_id=self.customer_id)

        # Slot raises DoesNotExist
        self.mock_slot_repo.select_for_update().get.side_effect = self.mock_slot_repo.model.DoesNotExist

        result = self.service.purchase_season_ticket(
            self.customer_id, self.vehicle_plate, self.slot_id, self.valid_from, self.valid_to
        )

        self.assertFalse(result["success"])
