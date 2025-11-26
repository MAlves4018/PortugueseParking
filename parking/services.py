from decimal import Decimal

from core.services import (AbstractPricingService,AbstractPaymentService)
from parking.models import ParkingSlot

from django.utils import timezone

from parking.data import SlotRepository, ContractRepository, MovementRepository

class PricingService(AbstractPricingService):
    """
    Concrete pricing service implementation.

    This service is responsible for calculating prices for:
    - season tickets (UC1 – purchase a season ticket)
    - occasional parking (used by occasional contracts / tickets)

    The pricing rules depend on:
    - the slot type (SIMPLE, EXTENDED, OVERSIZE)
    - whether the slot is accessible (for EXTENDED)
    """

    # Base prices for season tickets per slot category
    SEASON_PRICES = {
        "SIMPLE": Decimal("100.00"),
        "EXTENDED": Decimal("130.00"),
        "OVERSIZE": Decimal("160.00"),
    }

    # Base prices per hour for occasional parking per slot category
    OCCASIONAL_PRICES_PER_HOUR = {
        "SIMPLE": Decimal("3.00"),
        "EXTENDED": Decimal("4.50"),
        "OVERSIZE": Decimal("6.00"),
    }

    def __init__(self, slot_repo=None):
        """
        The slot_repo is injected to make the service testable.

        In production, this will normally be ParkingSlot.objects,
        but unit tests can pass a mock or a fake repository.
        """
        self._slot_repo = slot_repo or ParkingSlot.objects

    def _get_slot(self, slot_id: int) -> ParkingSlot:
        """
        Load the parking slot from the repository.

        This helper is used by both season and occasional pricing methods.
        """
        return self._slot_repo.get(pk=slot_id)

    def _get_pricing_category(self, slot: ParkingSlot) -> str:
        """
        Determine the pricing category for the given slot.

        Rules:
        - SIMPLE -> SIMPLE
        - OVERSIZE -> OVERSIZE
        - EXTENDED:
            - if the slot is accessible, we charge as SIMPLE
            - otherwise we charge as EXTENDED
        """
        code = slot.slot_type.code.upper()

        if code == "EXTENDED" and slot.is_accessible:
            return "SIMPLE"

        if code in {"SIMPLE", "EXTENDED", "OVERSIZE"}:
            return code

        # Fallback: treat unknown types as SIMPLE
        return "SIMPLE"

    def get_season_price(self, slot_id, period):
        """
        Calculate the season price for a given slot and period.

        According to the current lab scope, we ignore the actual
        duration of the period and only use a fixed base price per
        slot category. The period parameter is kept to stay aligned
        with the UML and to allow future extensions.
        """
        slot = self._get_slot(slot_id)
        category = self._get_pricing_category(slot)
        base_price = self.SEASON_PRICES[category]

        # For now we just return the base price.
        return float(base_price)

    def get_occasional_price(self, slot_id, duration_minutes: int):
        """
        Calculate the price for occasional parking.

        The price is computed as:
            rate_per_hour(category) * (duration_minutes / 60)

        This method will be used when computing the final price
        for occasional contracts and tickets (UC for occasional usage).
        """
        slot = self._get_slot(slot_id)
        category = self._get_pricing_category(slot)
        rate_per_hour = self.OCCASIONAL_PRICES_PER_HOUR[category]

        hours = Decimal(duration_minutes) / Decimal(60)
        amount = (hours * rate_per_hour).quantize(Decimal("0.01"))

        return float(amount)


class PaymentService(AbstractPaymentService):
    """
    Dummy payment service implementation.

    According to the project scope, we do not integrate with a real
    payment provider. For now every payment is considered successful.
    """

    def process_payment(self, customer_id, amount):
        """
        Process a payment for a given customer and amount.

        In this lab implementation, the payment is always successful.
        The method is kept to respect the service interface and to allow
        unit tests to mock different payment outcomes.
        """
        return True

class PricingService(AbstractPricingService):
    """
    Concrete pricing service implementation.

    This service is responsible for calculating prices for:
    - season tickets (UC1 – purchase a season ticket)
    - occasional parking (used by occasional contracts / tickets)

    The pricing rules depend on:
    - the slot type (SIMPLE, EXTENDED, OVERSIZE)
    - whether the slot is accessible (for EXTENDED)
    """

    SEASON_PRICES = {
        "SIMPLE": Decimal("100.00"),
        "EXTENDED": Decimal("130.00"),
        "OVERSIZE": Decimal("160.00"),
    }

    OCCASIONAL_PRICES_PER_HOUR = {
        "SIMPLE": Decimal("3.00"),
        "EXTENDED": Decimal("4.50"),
        "OVERSIZE": Decimal("6.00"),
    }

    def __init__(self, slot_repo=None):
        self._slot_repo = slot_repo or ParkingSlot.objects

    def _get_slot(self, slot_id: int) -> ParkingSlot:
        return self._slot_repo.get(pk=slot_id)

    def _get_pricing_category(self, slot: ParkingSlot) -> str:
        code = slot.slot_type.code.upper()

        if code == "EXTENDED" and slot.is_accessible:
            return "SIMPLE"

        if code in {"SIMPLE", "EXTENDED", "OVERSIZE"}:
            return code

        return "SIMPLE"

    def get_season_price(self, slot_id, period):
        slot = self._get_slot(slot_id)
        category = self._get_pricing_category(slot)
        base_price = self.SEASON_PRICES[category]
        return float(base_price)

    def get_occasional_price(self, slot_id, duration_minutes: int):
        slot = self._get_slot(slot_id)
        category = self._get_pricing_category(slot)
        rate_per_hour = self.OCCASIONAL_PRICES_PER_HOUR[category]

        hours = Decimal(duration_minutes) / Decimal(60)
        amount = (hours * rate_per_hour).quantize(Decimal("0.01"))

        return float(amount)


class PaymentService(AbstractPaymentService):
    """
    Dummy payment service implementation.

    According to the project scope, we do not integrate with a real
    payment provider. For now every payment is considered successful.
    """

    def process_payment(self, customer_id, amount):
        """
        Process a payment for a given customer and amount.

        In this lab implementation, the payment is always successful.
        The method is kept to respect the service interface and to allow
        unit tests to mock different payment outcomes.
        """
        return True


class SlotService:
    """
    Domain/application service responsible for slot management.

    Responsibilities:
    - Find slots that a given vehicle can use in a given period (UC1 support).
    - Verify that a specific slot is still available at confirmation time.
    - Provide simple occupancy statistics (current occupancy and usage summary).

    NOTE: This class does NOT perform any direct database queries.
    All data access is delegated to the repositories in parking.data.
    """

    def __init__(
        self,
        slot_repo: SlotRepository | None = None,
        contract_repo: ContractRepository | None = None,
        movement_repo: MovementRepository | None = None,
    ):
        # Default to real Django-backed repositories,
        # but allow injecting fakes/mocks in tests.
        self._slot_repo = slot_repo or SlotRepository()
        self._contract_repo = contract_repo or ContractRepository()
        self._movement_repo = movement_repo or MovementRepository()

    # ------------------------------------------------------------------
    # 1) Query: find available slots for a vehicle and period
    # ------------------------------------------------------------------
    def find_available_slots(self, vehicle, period, area=None):
        """
        Returns a list of ParkingSlot instances that:

        - Are in the given area (if provided),
        - Are compatible with the vehicle (size + accessibility),
        - Are free for the given period (no overlapping contracts).

        This corresponds to:
        - "System displays available parking slots from cache."
        - "System verifies slot availability."
        in UC1.
        """

        start, end = period

        # Get DB candidates via repository.
        candidates_qs = self._slot_repo.get_candidates_for_vehicle(vehicle, area)

        # Convert to list and apply domain logic on the objects.
        candidates = list(candidates_qs)

        available = []
        for slot in candidates:
            # 1) Check compatibility via domain method (size + accessibility).
            #    You can refine slot.is_compatible_with(vehicle) in ParkingSlot.
            if hasattr(slot, "is_compatible_with") and not slot.is_compatible_with(vehicle):
                continue

            # 2) Check if slot is free for the whole period.
            #    Uses the domain method implemented in ParkingSlot
            #    (which may itself hit the DB, but that's domain, not service).
            if not slot.is_free_for_period((start, end)):
                continue

            available.append(slot)

        return available

    # ------------------------------------------------------------------
    # 2) Command-like: verify slot availability at confirmation time
    # ------------------------------------------------------------------
    def verify_slot_available(self, slot_id, period):
        """
        Verifies if the slot is still free for the given period.

        Used in the confirmation step of UC1, where two users might
        concurrently pick the same slot.

        The repository deals with transaction & locking; the service
        simply interprets the result.
        """

        start, end = period

        # Lock slot row in the repository (select_for_update is inside the repo).
        slot = self._slot_repo.lock_slot(slot_id)

        overlapping_exists = self._contract_repo.has_overlapping_for_slot(
            slot, start, end
        )

        return {
            "slot": slot,
            "is_available": not overlapping_exists,
        }

    # ------------------------------------------------------------------
    # 3) Current occupancy statistics
    # ------------------------------------------------------------------
    def get_current_occupancy(self, at=None, area=None):
        """
        Returns a simple occupancy snapshot for a given timestamp.

        Metrics:
        - total_slots: number of slots considered
        - occupied_slots: slots currently occupied
        - occupancy_ratio: occupied_slots / total_slots

        The actual counting of occupied slots is delegated to the data layer.
        """

        at = at or timezone.now()

        slots_qs = self._slot_repo.get_slots_for_area(area)
        total_slots = slots_qs.count()

        if total_slots == 0:
            return {
                "total_slots": 0,
                "occupied_slots": 0,
                "occupancy_ratio": 0.0,
            }

        occupied_slots = self._movement_repo.count_occupied_slots_at(slots_qs, at)
        ratio = occupied_slots / total_slots

        return {
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "occupancy_ratio": ratio,
        }

    # ------------------------------------------------------------------
    # 4) Usage summary for a period (basis for more complex stats)
    # ------------------------------------------------------------------
    def get_usage_summary(self, period, area=None):
        """
        Returns a very simple usage summary for a given period.

        Current implementation:
        - counts movements that overlap the period,
        - aggregates total parked minutes.

        This is intentionally simple but shows how the domain model supports
        future statistics such as:
        - weekly/day-of-week occupancy patterns,
        - per-slot-type utilization,
        - reporting dashboards.
        """

        start, end = period

        movements = self._movement_repo.get_movements_overlapping_period(
            start, end, area
        )

        total_movements = movements.count()

        total_minutes = 0
        for m in movements:
            # Uses the domain method on Movement (duration_minutes),
            # which encapsulates the time difference logic.
            total_minutes += m.duration_minutes()

        return {
            "total_movements": total_movements,
            "total_parked_minutes": total_minutes,
        }