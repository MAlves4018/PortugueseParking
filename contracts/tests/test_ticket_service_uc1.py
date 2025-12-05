from django.test import TestCase
from unittest.mock import MagicMock

from core.services import ITicketService
from contracts.services import TicketService


class TicketServiceUC1Tests(TestCase):
    """
    UC1 – Purchase season ticket

    Service-level tests that isolate:
      - pricing service
      - payment service
      - persistence layer (repositories)
    """

    def setUp(self):
        self.pricing_service = MagicMock()
        self.payment_service = MagicMock()

        self.slot_repo = MagicMock()
        self.vehicle_repo = MagicMock()
        self.contract_repo = MagicMock()
        self.movement_repo = MagicMock()
        self.gate_repo = MagicMock()

        self.service: ITicketService = TicketService(
            pricing_service=self.pricing_service,
            payment_service=self.payment_service,
            slot_repo=self.slot_repo,
            vehicle_repo=self.vehicle_repo,
            contract_repo=self.contract_repo,
            movement_repo=self.movement_repo,
            gate_repo=self.gate_repo,
        )

    def test_purchase_season_ticket_success(self):
        """
        UC1 happy path:

        - slot is free (no overlapping contract)
        - payment succeeds
        - contract is created

        We verify that the service calls the collaborators correctly
        and returns a successful result.
        """

        customer_id = 1
        vehicle_plate = "AA-00-AA"
        slot_id = 42
        valid_from = "2025-01-01T08:00:00Z"
        valid_to = "2025-01-31T20:00:00Z"

        # Arrange mocks
        fake_vehicle = MagicMock()
        fake_slot = MagicMock()
        fake_contract = MagicMock(pk=123)

        # Vehicle and slot lookups (with select_for_update)
        self.vehicle_repo.select_for_update.return_value.get.return_value = fake_vehicle
        self.slot_repo.select_for_update.return_value.get.return_value = fake_slot

        # No overlapping contracts for this slot/period
        self.contract_repo.filter.return_value.exists.return_value = False

        # Pricing and payment
        self.pricing_service.get_season_price.return_value = 99.0
        self.payment_service.process_payment.return_value = True

        # Contract creation
        self.contract_repo.create.return_value = fake_contract

        # Act
        result = self.service.purchase_season_ticket(
            customer_id=customer_id,
            vehicle_plate=vehicle_plate,
            slot_id=slot_id,
            valid_from=valid_from,
            valid_to=valid_to,
        )

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["contract_id"], 123)

        self.pricing_service.get_season_price.assert_called_once()
        self.payment_service.process_payment.assert_called_once()
        self.contract_repo.create.assert_called_once()

    def test_purchase_season_ticket_fails_when_slot_overlapping(self):
        """
        UC1 negative path:

        - the selected slot already has an overlapping contract
        -> service must return error and must NOT:
           * calculate price
           * process payment
           * create a new contract
        """

        customer_id = 1
        vehicle_plate = "AA-00-AA"
        slot_id = 42
        valid_from = "2025-01-01T08:00:00Z"
        valid_to = "2025-01-31T20:00:00Z"

        # Vehicle and slot are still fetched (realistic behaviour)
        self.vehicle_repo.select_for_update.return_value.get.return_value = MagicMock()
        self.slot_repo.select_for_update.return_value.get.return_value = MagicMock()

        # There is an overlapping contract on this slot
        self.contract_repo.filter.return_value.exists.return_value = True

        # Act
        result = self.service.purchase_season_ticket(
            customer_id=customer_id,
            vehicle_plate=vehicle_plate,
            slot_id=slot_id,
            valid_from=valid_from,
            valid_to=valid_to,
        )

        # Assert
        self.assertFalse(result["success"])
        self.assertIn("Slot already reserved", result["reason"])

        self.pricing_service.get_season_price.assert_not_called()
        self.payment_service.process_payment.assert_not_called()
        self.contract_repo.create.assert_not_called()
