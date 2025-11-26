from django.db import models

class ParkingArea(models.Model):
    """
    Represents a physical parking area or level in the car park.
    This is master data and changes infrequently.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class SlotType(models.Model):
    """
    Represents the type of a parking slot (simple, extended, oversize, accessible, etc.).
    Pricing policies will later depend on this type.
    """

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    size_rank = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Relative size rank used for compatibility checks. "
            "For example: Simple=1, Extended=2, Oversize=3."
        ),
    )

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def can_host(self, required_type: "SlotType | None") -> bool:
        """
        Returns True if this SlotType is large enough to host the required_type.
        If required_type is None, any slot type is acceptable.
        """
        if required_type is None:
            return True
        return self.size_rank >= required_type.size_rank

class ParkingSlot(models.Model):
    """
    Represents an individual parking slot within a given parking area.
    """

    area = models.ForeignKey(
        ParkingArea,
        on_delete=models.CASCADE,
        related_name="slots",
    )
    number = models.CharField(max_length=20)
    slot_type = models.ForeignKey(
        SlotType,
        on_delete=models.PROTECT,
        related_name="slots",
    )
    is_accessible = models.BooleanField(default=False)

    def is_free_for_period(self, period, contract_qs=None):
        """
                Returns True if this slot is free for the given period.
        """
        start, end = period
        qs = contract_qs or self.contracts.all()
        return not qs.filter(
            valid_from__lt=end,
            valid_to__gt=start,
        ).exists()
################################################################NOTE THIS FUNCTION MAY NEED TO BE CHANGED AS IMPLEMENTATION GOES ON
    def is_compatible_with(self, vehicle: "Vehicle") -> bool:
        """
        Returns True if this slot is suitable for the given vehicle.

        Rules (can be refined later):
        - SlotType must be large enough for vehicle.minimum_slot_type.
        - If the slot is marked as accessible, the vehicle must have
          a disability permit (unless you decide accessible slots can
          also be used by others when free).
        """
        # Size/slot-type compatibility
        if not self.slot_type.can_host(vehicle.minimum_slot_type):
            return False

        # Accessibility rule
        if self.is_accessible and not vehicle.has_disability_permit:
            return False

        return True

    class Meta:
        unique_together = ("area", "number")
        ordering = ["area__name", "number"]

    def __str__(self) -> str:
        return f"{self.area.name} - {self.number} ({self.slot_type.code})"

class Gate(models.Model):
    """
    Represents a physical entry or exit gate in a parking area.
    """

    id = models.UUIDField(primary_key=True, editable=False)
    area = models.ForeignKey(
        ParkingArea,
        on_delete=models.CASCADE,
        related_name="gates",
    )
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.area.name} - {self.name}"
