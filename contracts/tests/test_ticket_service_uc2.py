from django.test import TestCase
from unittest.mock import MagicMock

from core.services import ITicketService
from contracts.services import TicketService


class TicketServiceUC2Tests(TestCase):
    """
    UC2 – Entry/exit with season ticket.

    Service-level tests only (no database, no views), using mocked
    repositories and collaborators.
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

    def test_enter_with_season_ticket_happy_path(self):
        """
        UC2 – entry with season ticket (happy path):

        - vehicle exists
        - there is an active contract for "now"
        - no open movement exists
        - gate exists

        -> service must create a movement and return open_gate=True
        """

        license_plate = "AA-00-AA"
        gate_id = "gate-1"

        fake_vehicle = MagicMock()
        self.vehicle_repo.get.return_value = fake_vehicle

        # Contract queryset: one active contract exists
        contract_qs = MagicMock()
        contract_qs.exists.return_value = True
        fake_contract = MagicMock()
        contract_qs.select_for_update.return_value.first.return_value = fake_contract
        self.contract_repo.filter.return_value = contract_qs

        # No open movement for this contract
        self.movement_repo.filter.return_value.exists.return_value = False

        # Valid gate
        fake_gate = MagicMock()
        self.gate_repo.get.return_value = fake_gate

        # Act
        result = self.service.enter_with_season_ticket(
            license_plate=license_plate,
            gate_id=gate_id,
        )

        # Assert
        self.assertTrue(result["success"])
        self.assertTrue(result["open_gate"])
        self.movement_repo.create.assert_called_once()

    def test_exit_with_season_ticket_no_open_movement(self):
        """
        UC2 – exit with season ticket, but no open movement:

        - vehicle exists
        - an active contract exists
        - there is NO movement with exit_time=None

        -> service must reject the exit and must NOT try to load the gate.
        """

        license_plate = "AA-00-AA"
        gate_id = "gate-1"

        fake_vehicle = MagicMock()
        self.vehicle_repo.get.return_value = fake_vehicle

        # Active contract returned by select_for_update().filter().first()
        fake_contract = MagicMock()
        (
            self.contract_repo
            .select_for_update
            .return_value
            .filter
            .return_value
            .first
            .return_value
        ) = fake_contract

        # No open movement for this contract
        (
            self.movement_repo
            .select_for_update
            .return_value
            .filter
            .return_value
            .order_by
            .return_value
            .first
            .return_value
        ) = None

        # Act
        result = self.service.exit_with_season_ticket(
            license_plate=license_plate,
            gate_id=gate_id,
        )

        # Assert
        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
        self.assertIn("No open entry", result["reason"])

        # Since there is no open movement, the gate should not even be validated
        self.gate_repo.get.assert_not_called()

    # --------- EXTRA TESTS FOR UC2 (ERROR PATHS) --------- #

    def test_enter_with_season_ticket_vehicle_not_found(self):
        """
        UC2 – entry with season ticket:

        If the vehicle with the given license plate does not exist,
        the service must deny entry and must not consult contracts.
        """

        license_plate = "AA-00-AA"
        gate_id = "gate-1"

        # Simulate Vehicle.objects.get(..., license_plate=...) raising DoesNotExist
        VehicleDoesNotExist = type("VehicleDoesNotExist", (Exception,), {})
        self.vehicle_repo.model.DoesNotExist = VehicleDoesNotExist
        self.vehicle_repo.get.side_effect = VehicleDoesNotExist

        result = self.service.enter_with_season_ticket(
            license_plate=license_plate,
            gate_id=gate_id,
        )

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
        self.assertIn("No vehicle with this license plate", result["reason"])

        # No contract lookup when vehicle cannot be found
        self.contract_repo.filter.assert_not_called()
        self.movement_repo.create.assert_not_called()

    def test_enter_with_season_ticket_gate_not_found(self):
        """
        UC2 – entry with season ticket:

        If the gate does not exist, the service must deny entry and
        must not create a movement.
        """

        license_plate = "AA-00-AA"
        gate_id = "gate-unknown"

        fake_vehicle = MagicMock()
        self.vehicle_repo.get.return_value = fake_vehicle

        # Active contract exists
        contract_qs = MagicMock()
        contract_qs.exists.return_value = True
        fake_contract = MagicMock()
        contract_qs.select_for_update.return_value.first.return_value = fake_contract
        self.contract_repo.filter.return_value = contract_qs

        # No open movement
        self.movement_repo.filter.return_value.exists.return_value = False

        # Gate .get() raises DoesNotExist
        GateDoesNotExist = type("GateDoesNotExist", (Exception,), {})
        self.gate_repo.model.DoesNotExist = GateDoesNotExist
        self.gate_repo.get.side_effect = GateDoesNotExist

        result = self.service.enter_with_season_ticket(
            license_plate=license_plate,
            gate_id=gate_id,
        )

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
        self.assertIn("Gate not found", result["reason"])

        # No movement should be created when gate does not exist
        self.movement_repo.create.assert_not_called()

    def test_enter_with_season_ticket_already_in_use(self):
        """
        UC2 – entry with season ticket:

        If there is already an open movement (ticket in use),
        the service must deny entry and must not touch the gate
        or create a new movement.
        """

        license_plate = "AA-00-AA"
        gate_id = "gate-1"

        fake_vehicle = MagicMock()
        self.vehicle_repo.get.return_value = fake_vehicle

        # Active contract exists
        contract_qs = MagicMock()
        contract_qs.exists.return_value = True
        fake_contract = MagicMock()
        contract_qs.select_for_update.return_value.first.return_value = fake_contract
        self.contract_repo.filter.return_value = contract_qs

        # Open movement already exists
        self.movement_repo.filter.return_value.exists.return_value = True

        result = self.service.enter_with_season_ticket(
            license_plate=license_plate,
            gate_id=gate_id,
        )

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
        self.assertIn("Season ticket already in use", result["reason"])

        # No gate lookup and no movement creation when already in use
        self.gate_repo.get.assert_not_called()
        self.movement_repo.create.assert_not_called()
