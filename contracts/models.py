import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from vehicles.models import Vehicle
from parking.models import ParkingSlot

class PaymentStatus(models.TextChoices):

    """
    Enumeration of payment statuses.
    """

    AUTHORIZED = "AUTHORIZED", "Authorized"
    PENDING = "PENDING", "Pending"
    SETTLED = "SETTLED", "Settled"
    FAILED = "FAILED", "Failed"


class Payment(models.Model):
    """
    Represents a payment associated with a movement or ticket.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movement_id = models.UUIDField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    performed_at = models.DateTimeField(null=True, blank=True)
    def settle(self) -> None:
        """
        Mark this payment as settled.
        """
        self.status = PaymentStatus.SETTLED
        self.performed_at = timezone.now()
        self.save()


class Contract(models.Model):
    """
    Base contract entity (parent for RegularContract and OccasionalContract).
    This model is concrete so that other models (e.g. Movement) can reference it.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    reserved_slot = models.ForeignKey(
        ParkingSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
    )

    class Meta:
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"

def __str__(self) -> str:
        return f"{self.__class__.__name__} for {self.vehicle} [{self.valid_from} - {self.valid_to}]"

    # Methods like isActive, hasOpenMovement, etc. will be added later.

class RegularContract(Contract):
    """
    Regular contract for long-term parking.
    """

    price = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="regular_contracts",
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="regular_contract",
    )

class OccasionalContract(Contract):
    """
    Occasional contract for single visits.
    """

    price = models.DecimalField(max_digits=10, decimal_places=2)

class Movement(models.Model):
    """
    Represents a parking movement (entry/exit) for a given contract.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="movements",
    )
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)

    def duration_minutes(self) -> int:
        """
        Returns the movement duration in minutes.
        """
        if not self.exit_time:
            return 0
        delta = self.exit_time - self.entry_time
        return int(delta.total_seconds() // 60)

class Ticket(models.Model):
    """
    Ticket for occasional contracts only.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.OneToOneField(
        OccasionalContract,
        on_delete=models.CASCADE,
        related_name="ticket",
    )
    issued_at = models.DateTimeField()
    deactivated_at = models.DateTimeField(null=True, blank=True)
    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ticket",
    )

    def is_active(self) -> bool:
        """
        Returns whether the ticket is currently active.
        """
        return self.deactivated_at is None
