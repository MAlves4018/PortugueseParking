from django.test import TestCase
from unittest.mock import MagicMock

from core.services import ITicketService
from contracts.services import TicketService


class TicketServiceTests(TestCase):
    """
    Unit tests for TicketService business logic.

    These tests isolate the service by mocking:
    - the pricing service
    - the payment service
    - the persistence layer (repositories)
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
        - slot is available
        - payment succeeds
        - contract is created

        We verify that the service calls the collaborators correctly
        and returns a successful result.
        """

        customer_id = 1
        vehicle_plate = "AA-00-AA"
        slot_id = 42
        valid_from = "dummy-from"
        valid_to = "dummy-to"

        # Arrange mocks
        fake_vehicle = MagicMock()
        fake_slot = MagicMock()
        fake_contract = MagicMock(pk=123)

        # vehicle and slot lookups
        self.vehicle_repo.select_for_update.return_value.get.return_value = fake_vehicle
        self.slot_repo.select_for_update.return_value.get.return_value = fake_slot

        # no overlapping contracts
        self.contract_repo.filter.return_value.exists.return_value = False

        # pricing and payment
        self.pricing_service.get_season_price.return_value = 99.0
        self.payment_service.process_payment.return_value = True

        # contract creation
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

    def test_entry_with_season_ticket_denied_when_no_contract(self):
        """
        UC2 negative path:
        - there is no active season ticket for the license plate.
        The service must deny entry and not create a movement.
        """

        license_plate = "AA-00-AA"
        gate_id = 10

        fake_vehicle = MagicMock()
        self.vehicle_repo.get.return_value = fake_vehicle
        self.contract_repo.filter.return_value.exists.return_value = False

        result = self.service.enter_with_season_ticket(
            license_plate=license_plate,
            gate_id=gate_id,
        )

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
        self.assertIn("No active season ticket", result["reason"])
        self.movement_repo.create.assert_not_called()
