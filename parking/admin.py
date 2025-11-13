from django.contrib import admin

from .models import ParkingArea, SlotType, ParkingSlot


@admin.register(ParkingArea)
class ParkingAreaAdmin(admin.ModelAdmin):
    """
    Admin configuration for ParkingArea.
    """

    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(SlotType)
class SlotTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for SlotType.
    """

    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    """
    Admin configuration for ParkingSlot.
    """

    list_display = ("area", "number", "slot_type", "is_accessible")
    list_filter = ("area", "slot_type", "is_accessible")
    search_fields = ("number",)

from .models import ParkingArea, SlotType, ParkingSlot, Gate

# ... existing admin classes ...

@admin.register(Gate)
class GateAdmin(admin.ModelAdmin):
    """
    Admin configuration for Gate.
    """

    list_display = ("area", "name")
    search_fields = ("name", "area__name")
    list_filter = ("area",)
