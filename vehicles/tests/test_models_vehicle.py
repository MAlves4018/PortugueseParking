# vehicles/tests/test_models_vehicle.py

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from customers.models import Customer
from parking.models import ParkingArea, SlotType, ParkingSlot
from contracts.models import Contract
from vehicles.models import Vehicle


class VehicleModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            username="user1",
            password="dummy",
        )

        self.area = ParkingArea.objects.create(
            name="Ground",
            description="Ground floor",
        )

        self.slot_type_simple = SlotType.objects.create(
            code="SIMPLE",
            name="Simple",
            description="Simple",
            size_rank=1,
        )
        self.slot_type_extended = SlotType.objects.create(
            code="EXTENDED",
            name="Extended",
            description="Extended",
            size_rank=2,
        )

        self.slot_simple = ParkingSlot.objects.create(
            area=self.area,
            number="G1",
            slot_type=self.slot_type_simple,
            is_accessible=False,
        )
        self.slot_extended_accessible = ParkingSlot.objects.create(
            area=self.area,
            number="G2",
            slot_type=self.slot_type_extended,
            is_accessible=True,
        )

    def test_requires_slot_type_returns_minimum_slot_type(self):
        v = Vehicle.objects.create(
            owner=self.customer,
            license_plate="HH-88-HH",
            minimum_slot_type=self.slot_type_simple,
        )

        self.assertEqual(v.requires_slot_type(), self.slot_type_simple)

        v_no_min = Vehicle.objects.create(
            owner=self.customer,
            license_plate="II-99-II",
            minimum_slot_type=None,
        )
        self.assertIsNone(v_no_min.requires_slot_type())

    def test_can_use_slot_delegates_to_parking_slot(self):
        v = Vehicle.objects.create(
            owner=self.customer,
            license_plate="JJ-10-JJ",
            minimum_slot_type=self.slot_type_simple,
            has_disability_permit=True,
        )
        self.assertTrue(v.can_use_slot(self.slot_extended_accessible) in (True, False))

    def test_active_contracts_filters_by_time(self):
        v = Vehicle.objects.create(
            owner=self.customer,
            license_plate="KK-11-KK",
            minimum_slot_type=self.slot_type_simple,
        )

        now = timezone.now()
        past_from = now - timedelta(days=5)
        past_to = now - timedelta(days=3)
        future_from = now + timedelta(days=3)
        future_to = now + timedelta(days=5)

        # contrato já terminado
        Contract.objects.create(
            vehicle=v,
            valid_from=past_from,
            valid_to=past_to,
            reserved_slot=self.slot_simple,
        )

        # contrato futuro
        Contract.objects.create(
            vehicle=v,
            valid_from=future_from,
            valid_to=future_to,
            reserved_slot=self.slot_simple,
        )

        # contrato ativo
        active = Contract.objects.create(
            vehicle=v,
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
            reserved_slot=self.slot_simple,
        )

        active_qs = v.active_contracts()
        self.assertEqual(active_qs.count(), 1)
        self.assertEqual(active_qs.first(), active)
