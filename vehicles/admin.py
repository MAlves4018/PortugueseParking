from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Vehicle model.

    Shows:
        - license plate,
        - disability permit flag,
        - oversize flag.
    """

    list_display = (
        "id",
        "license_plate",
        "owner",
        "minimum_slot_type",
        "has_disability_permit",
        "created_at",
    )

    list_filter = (
        "minimum_slot_type",
        "has_disability_permit",
        "owner",
    )

    search_fields = (
        "license_plate",
        "owner__username",
        "owner__first_name",
        "owner__last_name",
    )
