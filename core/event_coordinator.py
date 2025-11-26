from dataclasses import dataclass
from datetime import datetime


@dataclass
class FlowResult:
    """
    Wrapper returned by EventCoordinator in all flows.
    Allows the UI to react without knowing domain internals.
    """
    success: bool
    message: str
    data: dict | None = None


class EventCoordinator:
    """
    High-level application service coordinating all major use cases.
    This service does not implement business rules itself; instead,
    it orchestrates the specialised domain services:

        - TicketService
        - SlotService
        - PricingService
        - PaymentService

    This is the component that your colleague’s UI will call.
    """

    def __init__(
        self,
        ticket_service,
        slot_service,
        pricing_service,
        payment_service,
        vehicle_service=None,
    ):
        self.ticket_service = ticket_service
        self.slot_service = slot_service
        self.pricing_service = pricing_service
        self.payment_service = payment_service
        self.vehicle_service = vehicle_service

    # ============================================================
    # UC1 – Purchase Season Ticket
    # ============================================================

    def purchase_season_ticket_flow(
        self,
        customer_id,
        vehicle_plate,
        slot_id,
        valid_from: datetime,
        valid_to: datetime,
    ) -> FlowResult:
        """
        Full UC1 flow:

            1. Validate vehicle
            2. Check slot availability
            3. Validate vehicle-slot compatibility
            4. Compute price
            5. Process payment
            6. Create RegularContract via TicketService
        """

        # 1. Validate vehicle
        vehicle = self.vehicle_service.get_by_plate(vehicle_plate)
        if not vehicle:
            return FlowResult(False, "Vehicle not found.")

        # 2. Check availability
        period = (valid_from, valid_to)
        if not self.slot_service.verify_slot_available(slot_id, period):
            return FlowResult(False, "Selected slot is no longer available.")

        # 3. Compatibility
        if not self.slot_service.verify_vehicle_slot_compatibility(vehicle, slot_id):
            return FlowResult(False, "Vehicle incompatible with the chosen slot.")

        # 4. Pricing
        price = self.pricing_service.get_season_price(slot_id, period)

        # 5. Payment
        payment_ok = self.payment_service.process_payment(customer_id, price)
        if not payment_ok:
            return FlowResult(False, "Payment failed. Ticket not created.")

        # 6. Create contract (delegated!)
        contract = self.ticket_service.purchase_season_ticket(
            customer_id, vehicle_plate, slot_id, valid_from, valid_to
        )

        return FlowResult(
            True,
            "Season ticket successfully purchased.",
            {"contract_id": str(contract.id), "price": price},
        )

    # ============================================================
    # UC2 – Enter Parking with Season Ticket
    # ============================================================

    def enter_parking_flow(self, license_plate, gate_id) -> FlowResult:
        """
        Full UC2 flow:

            1. Find active season ticket (TicketService)
            2. Ensure no open movement
            3. Register entry (TicketService)
            4. Return gate instruction
        """

        result = self.ticket_service.enter_with_season_ticket(
            license_plate, gate_id
        )

        if not result["success"]:
            return FlowResult(False, result["message"])

        return FlowResult(True, "Gate opened.", data=result)
