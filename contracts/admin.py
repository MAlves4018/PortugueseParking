from django.contrib import admin
from .models import OccasionalTicket
from .models import (
    Payment,
    RegularContract,
    OccasionalContract,
    Movement,
    Ticket,
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Payment.
    """

    list_display = ("id", "amount", "status", "performed_at")
    list_filter = ("status",)
    search_fields = ("id",)


@admin.register(RegularContract)
class RegularContractAdmin(admin.ModelAdmin):
    """
    Admin configuration for RegularContract.
    """

    list_display = ("id", "vehicle", "customer", "valid_from", "valid_to", "price")
    list_filter = ("valid_from", "valid_to")
    search_fields = ("id", "vehicle__license_plate", "customer__username")


@admin.register(OccasionalContract)
class OccasionalContractAdmin(admin.ModelAdmin):
    """
    Admin configuration for OccasionalContract.
    """

    list_display = ("id", "vehicle", "valid_from", "valid_to", "price")
    list_filter = ("valid_from", "valid_to")
    search_fields = ("id", "vehicle__license_plate")


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    """
    Admin configuration for Movement.
    """

    list_display = ("id", "contract", "entry_time", "exit_time")
    list_filter = ("entry_time", "exit_time")
    search_fields = ("id",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Admin configuration for Ticket.
    """

    list_display = ("id", "contract", "issued_at", "deactivated_at")
    list_filter = ("issued_at",)
    search_fields = ("id",)

@admin.register(OccasionalTicket)
class OccasionalTicketAdmin(admin.ModelAdmin):
    list_display = ("license_plate", "slot", "entry_time", "exit_time", "amount_due", "amount_paid")
    search_fields = ("license_plate",)