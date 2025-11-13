# vehicles/models.py
from django.db import models
from customers.models import Customer

class Vehicle(models.Model):
    """
    Master data entity representing a registered vehicle.
    A vehicle:
      - belongs to a registered customer (owner),
      - is identified by its license plate,
      - may be marked as oversize (for oversize slots),
      - may have a disability permit (for accessible/discount rules).
    """

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

    is_oversize = models.BooleanField(
        default=False,
        help_text="True if this vehicle requires an oversize slot.",
    )

    has_disability_permit = models.BooleanField(
        default=False,
        help_text="True if the vehicle is allowed to use accessible slots with special pricing.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the vehicle was registered.",
    )

    class Meta:
        ordering = ["license_plate"]
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    def __str__(self) -> str:
        """
        Representation for admin and logs.
        """
        return f"{self.license_plate} ({self.owner})"
