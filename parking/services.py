from decimal import Decimal

from core.services import (
    AbstractPricingService,
    AbstractPaymentService,
)
from parking.models import ParkingSlot


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
