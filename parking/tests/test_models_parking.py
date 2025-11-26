# parking/tests/test_models_parking.py

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from customers.models import Customer
from vehicles.models import Vehicle
from parking.models import ParkingArea, SlotType, ParkingSlot, Gate
from contracts.models import Contract


class SlotTypeModelTests(TestCase):
    def test_can_host_none_always_true(self):
        t_simple = SlotType.objects.create(
            code="SIMPLE",
            name="Simple",
            description="Simple slot",
            size_rank=1,
        )
        self.assertTrue(t_simple.can_host(None))

    def test_can_host_based_on_size_rank(self):
        t_simple = SlotType.objects.create(
            code="SIMPLE",
            name="Simple",
            description="Simple slot",
            size_rank=1,
        )
        t_extended = SlotType.objects.create(
            code="EXTENDED",
            name="Extended",
            description="Extended slot",
            size_rank=2,
        )
        t_oversize = SlotType.objects.create(
            code="OVERSIZE",
            name="Oversize",
            description="Oversize slot",
            size_rank=3,
        )

        # Extended pode receber Simple
        self.assertTrue(t_extended.can_host(t_simple))
        # Simple não pode receber Extended
        self.assertFalse(t_simple.can_host(t_extended))
        # Oversize pode receber qualquer um
        self.assertTrue(t_oversize.can_host(t_simple))
        self.assertTrue(t_oversize.can_host(t_extended))


class ParkingSlotModelTests(TestCase):
    def setUp(self):
        self.area = ParkingArea.objects.create(
            name="Main",
            description="Main area",
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
            number="S1",
            slot_type=self.slot_type_simple,
            is_accessible=False,
        )
        self.slot_extended_accessible = ParkingSlot.objects.create(
            area=self.area,
            number="E1",
            slot_type=self.slot_type_extended,
            is_accessible=True,
        )

        self.customer = Customer.objects.create_user(
            username="eva",
            password="dummy",
        )

        self.vehicle_simple = Vehicle.objects.create(
            owner=self.customer,
            license_plate="EE-55-EE",
            minimum_slot_type=self.slot_type_simple,
            has_disability_permit=False,
        )

        self.vehicle_extended = Vehicle.objects.create(
            owner=self.customer,
            license_plate="FF-66-FF",
            minimum_slot_type=self.slot_type_extended,
            has_disability_permit=False,
        )

        self.vehicle_with_permit = Vehicle.objects.create(
            owner=self.customer,
            license_plate="GG-77-GG",
            minimum_slot_type=self.slot_type_extended,
            has_disability_permit=True,
        )

    def test_is_free_for_period_without_contracts(self):
        now = timezone.now()
        period = (now, now + timedelta(hours=1))

        self.assertTrue(self.slot_simple.is_free_for_period(period))

    def test_is_free_for_period_with_overlapping_contract(self):
        now = timezone.now()
        period = (now, now + timedelta(hours=1))

        contract = Contract.objects.create(
            vehicle=self.vehicle_simple,
            valid_from=now - timedelta(minutes=30),
            valid_to=now + timedelta(minutes=30),
            reserved_slot=self.slot_simple,
        )

        self.assertFalse(self.slot_simple.is_free_for_period(period))

        # período completamente antes do contrato → livre
        before_period = (now - timedelta(hours=3), now - timedelta(hours=2))
        self.assertTrue(self.slot_simple.is_free_for_period(before_period))

        # período completamente depois do contrato → livre
        after_period = (now + timedelta(hours=2), now + timedelta(hours=3))
        self.assertTrue(self.slot_simple.is_free_for_period(after_period))

    def test_is_compatible_with_size_and_accessibility_rules(self):
        # veículo simples pode usar slot simples não acessível
        self.assertTrue(self.slot_simple.is_compatible_with(self.vehicle_simple))

        # veículo extended não pode usar slot simples (size_rank insuficiente)
        self.assertFalse(self.slot_simple.is_compatible_with(self.vehicle_extended))

        # slot acessível + veículo sem disability_permit → não pode
        self.assertFalse(
            self.slot_extended_accessible.is_compatible_with(self.vehicle_extended)
        )

        # slot acessível + veículo COM disability_permit → pode
        self.assertTrue(
            self.slot_extended_accessible.is_compatible_with(
                self.vehicle_with_permit
            )
        )


class GateModelTests(TestCase):
    def test_str_representation(self):
        area = ParkingArea.objects.create(
            name="Side",
            description="Side entrance",
        )
        gate = Gate.objects.create(
            id="123e4567-e89b-12d3-a456-426614174000",
            area=area,
            name="North Gate",
        )

        self.assertIn("Side", str(gate))
        self.assertIn("North Gate", str(gate))
