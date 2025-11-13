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
        "has_disability_permit",
        "is_oversize",
    )

    list_filter = (
        "has_disability_permit",
        "is_oversize",
    )

    search_fields = (
        "license_plate",
        "owner__username",
    )
