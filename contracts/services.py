from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from core.services import ITicketService, IPricingService, IPaymentService
from contracts.models import RegularContract, Movement
from vehicles.models import Vehicle
from parking.models import ParkingSlot, Gate
from parking.services import PricingService, PaymentService
from django.db.models import Exists, OuterRef
from .models import RegularContract, OccasionalTicket
from parking.models import ParkingSlot

GRACE_PERIOD_MINUTES = 15

class TicketService(ITicketService):
    """
    Ticket service implementing the business logic for:

    - UC1: Purchase a season ticket
    - UC2: Entry with season ticket

    The service interacts with:
    - persistence (Django models) via injected repositories
    - pricing service
    - payment service
    """

    def __init__(
        self,
        pricing_service: IPricingService,
        payment_service: IPaymentService,
        slot_repo=None,
        vehicle_repo=None,
        contract_repo=None,
        movement_repo=None,
        gate_repo=None,
    ):
        """
        All collaborators are injected to make the service easy to test.

        In production, the repos will be Django ORM managers (e.g. ParkingSlot.objects),
        but in unit tests we can replace them with mocks or in-memory fakes.
        """
        self.pricing_service = pricing_service
        self.payment_service = payment_service

        # Default repositories use the Django ORM managers
        self._slot_repo = slot_repo or ParkingSlot.objects
        self._vehicle_repo = vehicle_repo or Vehicle.objects
        self._contract_repo = contract_repo or RegularContract.objects
        self._movement_repo = movement_repo or Movement.objects
        self._gate_repo = gate_repo or Gate.objects

    @transaction.atomic
    def purchase_season_ticket(
        self,
        customer_id,
        vehicle_plate,
        slot_id,
        valid_from,
        valid_to,
    ):
        """
        UC1: Purchase a season ticket.

        This method implements the main business logic described in the UC:
        - verify slot availability
        - compute the price
        - process the payment
        - create a regular contract and reserve the slot
        - guarantee atomicity using a database transaction
        """

        # 1) Load vehicle and slot
        normalized_plate = vehicle_plate.strip().upper()
        vehicle = self._vehicle_repo.select_for_update().get(
            owner_id=customer_id,
            license_plate=normalized_plate,
        )
        slot = self._slot_repo.select_for_update().get(pk=slot_id)

        # 2) Check that there is no overlapping contract on this slot
        overlapping = self._contract_repo.filter(
            reserved_slot=slot,
            valid_from__lt=valid_to,
            valid_to__gt=valid_from,
        ).exists()

        if overlapping:
            return {
                "success": False,
                "reason": "Slot already reserved for the selected period.",
            }

        # 3) Calculate price using pricing service
        price = self.pricing_service.get_season_price(
            slot_id=slot_id,
            period=(valid_from, valid_to),
        )

        # 4) Process payment
        payment_success = self.payment_service.process_payment(
            customer_id=customer_id,
            amount=price,
        )
        if not payment_success:
            return {
                "success": False,
                "reason": "Payment failed.",
            }

        # 5) Create regular contract (the season ticket)
        contract = self._contract_repo.create(
            vehicle=vehicle,
            customer=vehicle.owner,
            valid_from=valid_from,
            valid_to=valid_to,
            reserved_slot=slot,
            price = price,
        )

        return {
            "success": True,
            "reason": "Season ticket created successfully.",
            "contract_id": contract.pk,
        }

    def enter_with_season_ticket(
        self,
        license_plate,
        gate_id,
    ):
        """
        UC2: Entry with season ticket.

        - Identify the vehicle and its active season ticket by license plate.
        - Ensure the ticket is not already in use.
        - Record the entry movement and instruct the gate to open.
        """

        now = timezone.now()
        normalized_plate = license_plate.strip().upper()
        # 1) Find vehicle by license plate
        try:
            vehicle = self._vehicle_repo.get(license_plate=normalized_plate)
        except self._vehicle_repo.model.DoesNotExist:
            return {
                "success": False,
                "open_gate": False,
                "reason": "No vehicle with this license plate.",
            }

        # 2) Find active regular contract for this vehicle
        contract_qs = self._contract_repo.filter(
            vehicle=vehicle,
            valid_from__lte=now,
            valid_to__gte=now,
        )
        if not contract_qs.exists():
            return {
                "success": False,
                "open_gate": False,
                "reason": "No active season ticket for this license plate.",
            }

        contract = contract_qs.select_for_update().first()

        # 3) Check if there is already an open movement
        open_movement_exists = self._movement_repo.filter(
            contract=contract,
            exit_time__isnull=True,
        ).exists()

        if open_movement_exists:
            return {
                "success": False,
                "open_gate": False,
                "reason": "Season ticket already in use.",
            }

        # 4) Validate gate
        try:
            gate = self._gate_repo.get(pk=gate_id)
        except self._gate_repo.model.DoesNotExist:
            return {
                "success": False,
                "open_gate": False,
                "reason": "Gate not found.",
            }

        # 5) Only now create movement
        movement = self._movement_repo.create(
            contract=contract,
            entry_time=now,
        )

        return {
            "success": True,
            "open_gate": True,
            "reason": "Entry granted.",
            "movement_id": movement.pk,
        }

    def exit_with_season_ticket(self, license_plate, gate_id):
        """
        Handles exit with a season ticket:

        - Find vehicle by license plate
        - Find active contract
        - Find open movement (no exit_time)
        - Close movement and open gate
        """
        now = timezone.now()
        normalized_plate = license_plate.strip().upper()

        with transaction.atomic():
            # 1) Find vehicle
            try:
                vehicle = self._vehicle_repo.get(license_plate=normalized_plate)
            except self._vehicle_repo.model.DoesNotExist:
                return {
                    "success": False,
                    "open_gate": False,
                    "reason": "No vehicle with this license plate.",
                }

            # 2) Active season contract
            contract = (
                self._contract_repo
                .select_for_update()
                .filter(
                    vehicle=vehicle,
                    valid_from__lte=now,
                    valid_to__gte=now,
                )
                .first()
            )
            if not contract:
                return {
                    "success": False,
                    "open_gate": False,
                    "reason": "No active season ticket for this vehicle.",
                }

            # 3) Open movement
            movement = (
                self._movement_repo
                .select_for_update()
                .filter(contract=contract, exit_time__isnull=True)
                .order_by("-entry_time")
                .first()
            )
            if not movement:
                return {
                    "success": False,
                    "open_gate": False,
                    "reason": "No open entry for this ticket.",
                }

            # 4) Validate gate
            try:
                gate = self._gate_repo.get(pk=gate_id)
            except self._gate_repo.model.DoesNotExist:
                return {
                    "success": False,
                    "open_gate": False,
                    "reason": "Gate not found.",
                }

            # 5) Close movement
            movement.exit_time = now
            movement.save(update_fields=["exit_time"])

        return {
            "success": True,
            "open_gate": True,
            "reason": "Exit granted.",
            "movement_id": movement.pk,
        }
    
    #--------Occasional Ticket Methods--------#
    @transaction.atomic
    def start_occasional_entry(self, license_plate: str, gate_id) -> dict:
        """
        Creates an anonymous single-use ticket for an occasional customer.

        - Finds a free slot (no active season contract now, no open occasional ticket)
        - Records entry_time
        """
        normalized_plate = license_plate.strip().upper()
        now = timezone.now()

        active_contracts = RegularContract.objects.filter(
            reserved_slot=OuterRef("pk"),
            valid_from__lte=now,
            valid_to__gte=now,
        )

        open_occasional = OccasionalTicket.objects.filter(
            slot=OuterRef("pk"),
            is_closed=False,
        )

        free_slot = (
            ParkingSlot.objects
            .select_for_update()
            .select_related("slot_type", "area")
            .annotate(
                has_season=Exists(active_contracts),
                has_open_occasional=Exists(open_occasional),
            )
            .filter(has_season=False, has_open_occasional=False)
            .order_by("slot_type__code", "area__name", "number")
            .first()
        )

        if not free_slot:
            return {
                "success": False,
                "reason": "No free slot available for occasional customers.",
            }

        ticket = OccasionalTicket.objects.create(
            license_plate=normalized_plate,
            slot=free_slot,
            entry_time=now,
        )

        return {
            "success": True,
            "ticket_id": str(ticket.id),
            "slot_label": f"{free_slot.area.name} / {free_slot.number}",
            "reason": "Ticket issued. Please proceed to parking.",
        }

    # ---------- OCCASIONAL PRICING (CASH DEVICE) ----------

    def get_occasional_pricing(self, license_plate: str) -> dict:
        """
        Used by the cash device:

        - finds the open occasional ticket (no exit_time, not closed)
        - calculates amount_due based on duration & slot type
        """
        normalized_plate = license_plate.strip().upper()
        now = timezone.now()

        ticket = (
            OccasionalTicket.objects
            .select_related("slot", "slot__slot_type")
            .filter(license_plate=normalized_plate, is_closed=False)
            .order_by("-entry_time")
            .first()
        )
        if not ticket:
            return {
                "success": False,
                "reason": "No active occasional ticket found for this license plate.",
            }

        duration = now - ticket.entry_time
        duration_minutes = int(duration.total_seconds() // 60)

        amount = self.pricing_service.get_occasional_price(
            slot_id=ticket.slot.id,
            duration_minutes=duration_minutes,
        )

        ticket.amount_due = amount
        ticket.save(update_fields=["amount_due"])

        return {
            "success": True,
            "ticket": ticket,
            "amount": amount,
            "duration_minutes": int(duration.total_seconds() // 60),
        }

    # ---------- OCCASIONAL PAYMENT ----------

    @transaction.atomic
    def pay_occasional_ticket(self, license_plate: str) -> dict:
        """
        Called by cash device when customer confirms payment.
        """
        normalized_plate = license_plate.strip().upper()

        pricing_info = self.get_occasional_pricing(normalized_plate)
        if not pricing_info["success"]:
            return pricing_info

        ticket = pricing_info["ticket"]
        amount = pricing_info["amount"]

        # process payment via PaymentService (mock)
        payment_ok = self.payment_service.process_payment(
            customer_id=None,  # anonymous
            amount=amount,
        )
        if not payment_ok:
            return {
                "success": False,
                "reason": "Payment failed. Please try again.",
            }

        now = timezone.now()
        ticket.amount_paid = amount
        ticket.paid_at = now
        ticket.exit_deadline = now + timedelta(minutes=GRACE_PERIOD_MINUTES)
        ticket.save(update_fields=["amount_paid", "paid_at", "exit_deadline"])

        return {
            "success": True,
            "ticket": ticket,
            "amount": amount,
            "deadline": ticket.exit_deadline,
            "reason": "Payment successful. Please exit within 15 minutes.",
        }

    # ---------- OCCASIONAL EXIT ----------
    @transaction.atomic
    def exit_with_occasional_ticket(self, license_plate: str, gate_id) -> dict:
        """
        Validates exit for occasional customers:

        - ticket must exist and be paid
        - must still be within grace period
        - marks exit & closes ticket
        """
        normalized_plate = license_plate.strip().upper()
        now = timezone.now()

        ticket = (
            OccasionalTicket.objects
            .select_for_update()
            .select_related("slot")
            .filter(license_plate=normalized_plate, is_closed=False)
            .order_by("-entry_time")
            .first()
        )
        if not ticket:
            return {
                "success": False,
                "open_gate": False,
                "reason": "No active occasional ticket for this license plate.",
            }

        if not ticket.is_paid:
            return {
                "success": False,
                "open_gate": False,
                "reason": "Ticket not paid. Please pay at the cash device.",
            }

        if not ticket.is_within_grace_period:
            ticket.amount_due = 0
            ticket.amount_paid = 0
            ticket.paid_at = None
            ticket.exit_deadline = None
            ticket.save(update_fields=["amount_due", "amount_paid", "paid_at", "exit_deadline"])

            return {
                "success": False,
                "open_gate": False,
                "reason": "Grace period expired. Additional payment required.",
            }

        ticket.exit_time = now
        ticket.is_closed = True
        ticket.save(update_fields=["exit_time", "is_closed"])

        return {
            "success": True,
            "open_gate": True,
            "reason": "Exit granted. Thank you for your visit.",
        }
