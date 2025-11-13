from django.test import TestCase

from parking.models import ParkingArea, SlotType, ParkingSlot


class ParkingModelTests(TestCase):
    """
    Unit tests for the basic parking master data models.
    """

    def test_create_and_reload_parking_area(self):
        # Create and persist a ParkingArea
        area = ParkingArea.objects.create(
            name="Level -1",
            description="Underground level -1",
        )

        # Reload from database
        loaded = ParkingArea.objects.get(pk=area.pk)

        # Check validity
        self.assertEqual(loaded.name, "Level -1")
        self.assertEqual(loaded.description, "Underground level -1")
        self.assertEqual(str(loaded), "Level -1")

    def test_parking_slot_associations(self):
        # Create related master data
        area = ParkingArea.objects.create(
            name="Level 0",
            description="Ground floor",
        )
        slot_type = SlotType.objects.create(
            code="SIMPLE",
            name="Simple slot",
            description="Standard size slot",
        )

        # Create and persist a ParkingSlot
        slot = ParkingSlot.objects.create(
            area=area,
            number="A-01",
            slot_type=slot_type,
            is_accessible=False,
        )

        # Reload from database
        loaded = ParkingSlot.objects.get(pk=slot.pk)

        # Check basic fields
        self.assertEqual(loaded.number, "A-01")
        self.assertFalse(loaded.is_accessible)

        # Check associations are valid
        self.assertEqual(loaded.area.pk, area.pk)
        self.assertEqual(loaded.slot_type.pk, slot_type.pk)
        self.assertEqual(loaded.area.name, "Level 0")
        self.assertEqual(loaded.slot_type.code, "SIMPLE")
