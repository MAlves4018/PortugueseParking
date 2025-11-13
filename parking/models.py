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

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


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
