# contracts/tests/test_models_contracts.py

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from customers.models import Customer
from vehicles.models import Vehicle
from parking.models import ParkingArea, SlotType, ParkingSlot
from contracts.models import (
    Payment,
    PaymentStatus,
    Contract,
    RegularContract,
    OccasionalContract,
    Movement,
    Ticket,
)


class PaymentModelTests(TestCase):
    def test_settle_updates_status_and_timestamp(self):
        payment = Payment.objects.create(
            amount=10.00,
            status=PaymentStatus.PENDING,
        )

        self.assertEqual(payment.status, PaymentStatus.PENDING)
        self.assertIsNone(payment.performed_at)

        payment.settle()
        payment.refresh_from_db()

        self.assertEqual(payment.status, PaymentStatus.SETTLED)
        self.assertIsNotNone(payment.performed_at)


class ContractModelTests(TestCase):
    def setUp(self):
        # Customer + Vehicle + ParkingSlot mínimos para construir um Contract
        self.customer = Customer.objects.create_user(
            username="john",
            password="dummy",
        )

        self.area = ParkingArea.objects.create(
            name="Main",
            description="Main parking area",
        )

        self.slot_type = SlotType.objects.create(
            code="SIMPLE",
            name="Simple",
            description="Simple slot",
            size_rank=1,
        )

        self.slot = ParkingSlot.objects.create(
            area=self.area,
            number="A1",
            slot_type=self.slot_type,
            is_accessible=False,
        )

        self.vehicle = Vehicle.objects.create(
            owner=self.customer,
            license_plate="AA-11-AA",
        )

        now = timezone.now()
        self.valid_from = now - timedelta(days=1)
        self.valid_to = now + timedelta(days=1)

        self.contract = Contract.objects.create(
            vehicle=self.vehicle,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            reserved_slot=self.slot,
        )

    def test_is_active_inside_period(self):
        at = timezone.now()
        self.assertTrue(self.contract.is_active(at))

    def test_is_active_before_period(self):
        at = self.valid_from - timedelta(seconds=1)
        self.assertFalse(self.contract.is_active(at))

    def test_is_active_after_period(self):
        at = self.valid_to + timedelta(seconds=1)
        self.assertFalse(self.contract.is_active(at))

    def test_has_open_movement_and_get_active_movement(self):
        # Sem movimentos → nada aberto
        self.assertFalse(self.contract.has_open_movement())
        self.assertIsNone(self.contract.get_active_movement())

        # Movimento fechado
        Movement.objects.create(
            contract=self.contract,
            entry_time=timezone.now() - timedelta(hours=2),
            exit_time=timezone.now() - timedelta(hours=1),
        )
        self.assertFalse(self.contract.has_open_movement())
        self.assertIsNone(self.contract.get_active_movement())

        # Movimento aberto
        open_movement = Movement.objects.create(
            contract=self.contract,
            entry_time=timezone.now() - timedelta(minutes=30),
            exit_time=None,
        )

        self.assertTrue(self.contract.has_open_movement())
        self.assertEqual(self.contract.get_active_movement(), open_movement)

    def test_total_parked_minutes_aggregates_movements(self):
        now = timezone.now()

        Movement.objects.create(
            contract=self.contract,
            entry_time=now - timedelta(minutes=60),
            exit_time=now - timedelta(minutes=30),
        )  # 30 min

        Movement.objects.create(
            contract=self.contract,
            entry_time=now - timedelta(minutes=20),
            exit_time=now - timedelta(minutes=5),
        )  # 15 min

        # Movimento aberto não deve somar tempo (duration_minutes = 0)
        Movement.objects.create(
            contract=self.contract,
            entry_time=now - timedelta(minutes=3),
            exit_time=None,
        )

        total = self.contract.total_parked_minutes()
        self.assertEqual(total, 45)


class RegularAndOccasionalContractTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            username="alice",
            password="dummy",
        )

        self.area = ParkingArea.objects.create(
            name="Level1",
            description="Level 1",
        )
        self.slot_type = SlotType.objects.create(
            code="EXTENDED",
            name="Extended",
            description="Extended slot",
            size_rank=2,
        )
        self.slot = ParkingSlot.objects.create(
            area=self.area,
            number="B1",
            slot_type=self.slot_type,
            is_accessible=False,
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.customer,
            license_plate="BB-22-BB",
        )

        now = timezone.now()
        self.period = (now - timedelta(days=1), now + timedelta(days=1))

    def test_regular_contract_creation_and_basic_fields(self):
        contract = RegularContract.objects.create(
            vehicle=self.vehicle,
            valid_from=self.period[0],
            valid_to=self.period[1],
            reserved_slot=self.slot,
            price=50.00,
            customer=self.customer,
        )

        self.assertTrue(contract.is_active())
        self.assertEqual(contract.price, 50.00)
        self.assertEqual(contract.customer, self.customer)

    def test_occasional_contract_creation_and_basic_fields(self):
        contract = OccasionalContract.objects.create(
            vehicle=self.vehicle,
            valid_from=self.period[0],
            valid_to=self.period[1],
            reserved_slot=self.slot,
            price=7.50,
        )

        self.assertTrue(contract.is_active())
        self.assertEqual(contract.price, 7.50)


class MovementModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            username="bob",
            password="dummy",
        )
        self.area = ParkingArea.objects.create(
            name="OpenAir",
            description="Outdoor area",
        )
        self.slot_type = SlotType.objects.create(
            code="SIMPLE",
            name="Simple",
            description="Simple slot",
            size_rank=1,
        )
        self.slot = ParkingSlot.objects.create(
            area=self.area,
            number="C1",
            slot_type=self.slot_type,
            is_accessible=False,
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.customer,
            license_plate="CC-33-CC",
        )
        now = timezone.now()
        self.contract = Contract.objects.create(
            vehicle=self.vehicle,
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
            reserved_slot=self.slot,
        )

    def test_duration_minutes_open_movement_zero(self):
        m = Movement.objects.create(
            contract=self.contract,
            entry_time=timezone.now() - timedelta(minutes=10),
            exit_time=None,
        )
        self.assertEqual(m.duration_minutes(), 0)
        self.assertTrue(m.is_open())

    def test_duration_minutes_closed_movement(self):
        entry = timezone.now() - timedelta(minutes=30)
        exit_ = entry + timedelta(minutes=18)
        m = Movement.objects.create(
            contract=self.contract,
            entry_time=entry,
            exit_time=exit_,
        )
        self.assertEqual(m.duration_minutes(), 18)
        self.assertFalse(m.is_open())


class TicketModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            username="dave",
            password="dummy",
        )
        self.area = ParkingArea.objects.create(
            name="RoofTop",
            description="Roof top area",
        )
        self.slot_type = SlotType.objects.create(
            code="SIMPLE",
            name="Simple",
            description="Simple",
            size_rank=1,
        )
        self.slot = ParkingSlot.objects.create(
            area=self.area,
            number="R1",
            slot_type=self.slot_type,
            is_accessible=False,
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.customer,
            license_plate="DD-44-DD",
        )
        now = timezone.now()
        self.contract = OccasionalContract.objects.create(
            vehicle=self.vehicle,
            valid_from=now - timedelta(hours=1),
            valid_to=now + timedelta(hours=1),
            reserved_slot=self.slot,
            price=5.00,
        )

    def test_ticket_is_active_and_deactivated(self):
        now = timezone.now()
        ticket = Ticket.objects.create(
            contract=self.contract,
            issued_at=now,
            deactivated_at=None,
        )

        self.assertTrue(ticket.is_active())

        ticket.deactivated_at = now + timedelta(minutes=10)
        ticket.save()

        self.assertFalse(ticket.is_active())
