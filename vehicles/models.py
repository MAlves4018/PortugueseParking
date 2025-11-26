# vehicles/models.py
import uuid
from django.conf import settings
from django.db import models
from customers.models import Customer
from parking.models import ParkingSlot


# String reference to avoid hard import cycle;
# SlotType is defined in parking.models and both ParkingSlot and Vehicle should use the same table for slot types.
# from parking.models import SlotType  # not needed if we use "parking.SlotType" string

class Vehicle(models.Model):
    """
    Master data entity representing a registered vehicle.
    A vehicle:
      - belongs to a registered customer (owner),
      - is identified by its license plate,
      - may be marked as oversize (for oversize slots),
      - may have a disability permit (for accessible/discount rules).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Stable UUID primary key for the vehicle.",
    )

    owner = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="vehicles",
        help_text="Customer who owns this vehicle.",
    )

    license_plate = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique license plate identifier used at the gate.",
    )

    minimum_slot_type = models.ForeignKey(
        "parking.SlotType",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="vehicles",
        help_text=(
            "Minimum slot type this vehicle requires (e.g. Simple, Extended, Oversize). "
            "This should use the same SlotType records as ParkingSlot."
        ),
    )

    has_disability_permit = models.BooleanField(
        default=False,
        help_text="True if the vehicle is allowed to use accessible slots with special pricing.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the vehicle was registered.",
    )

    def requires_slot_type(self):
        """
        Returns the minimum slot type this vehicle needs.
        """
        return self.minimum_slot_type

    def can_use_slot(self, slot: "ParkingSlot") -> bool:
        """
        Convenience wrapper that delegates to ParkingSlot for compatibility check.
        This keeps business rules in one place and makes the domain expressive.
        """
        return slot.is_compatible_with(self)

    def active_contracts(self, at=None):
        """
        Returns all contracts of this vehicle that are active at the given time.
        """
        from django.utils import timezone
        at = at or timezone.now()
        return self.contracts.filter(valid_from__lte=at, valid_to__gte=at)

    class Meta:
        ordering = ["license_plate"]
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        swappable = "VEHICLE_MODEL"

    def __str__(self) -> str:
        """
        Representation for admin and logs.
        """
        return f"{self.license_plate} ({self.owner})"
