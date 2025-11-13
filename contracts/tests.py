import uuid

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from vehicles.models import Vehicle
from parking.models import ParkingArea, SlotType, ParkingSlot
from contracts.models import RegularContract, Payment, Movement


User = get_user_model()


class ContractModelTests(TestCase):
    """
    Unit tests for contract-related models.
    """

    def setUp(self):
        self.customer = User.objects.create(
            username="john",
            email="john@example.com",
        )
        self.customer.set_password("test1234")
        self.customer.save()

        self.area = ParkingArea.objects.create(name="Level 0", description="")
        self.slot_type = SlotType.objects.create(code="SIMPLE", name="Simple", description="")
        self.slot = ParkingSlot.objects.create(
            area=self.area,
            number="A-01",
            slot_type=self.slot_type,
            is_accessible=False,
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.customer,
            license_plate="AA-00-AA",
        )

    def test_create_and_reload_regular_contract(self):
        payment = Payment.objects.create(amount=10.0)

        contract = RegularContract.objects.create(
            vehicle=self.vehicle,
            customer=self.customer,
            valid_from=timezone.now(),
            valid_to=timezone.now(),
            reserved_slot=self.slot,
            price=10.0,
            payment=payment,
        )

        loaded = RegularContract.objects.get(pk=contract.pk)

        self.assertEqual(loaded.vehicle.license_plate, "AA-00-AA")
        self.assertEqual(loaded.customer.username, "john")
        self.assertEqual(loaded.reserved_slot.number, "A-01")
        self.assertEqual(loaded.price, contract.price)

    def test_movement_associations(self):
        contract = RegularContract.objects.create(
            vehicle=self.vehicle,
            customer=self.customer,
            valid_from=timezone.now(),
            valid_to=timezone.now(),
            reserved_slot=self.slot,
            price=10.0,
        )

        movement = Movement.objects.create(
            contract=contract,
            entry_time=timezone.now(),
        )

        loaded = Movement.objects.get(pk=movement.pk)

        # Check direct association
        self.assertEqual(loaded.contract.pk, contract.pk)

        # Check transitive associations
        self.assertEqual(loaded.contract.regularcontract.vehicle.pk, self.vehicle.pk)
        self.assertEqual(loaded.contract.regularcontract.customer.pk, self.customer.pk)
        self.assertEqual(loaded.contract.regularcontract.reserved_slot.pk, self.slot.pk)