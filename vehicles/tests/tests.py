# vehicles/tests.py

from django.test import TestCase

from customers.models import Customer
from vehicles.models import Vehicle
from vehicles.services import VehicleService


class VehicleModelTests(TestCase):
    """
    Basic persistence tests for the Vehicle model.

    The goal is to verify that:
      - vehicles can be created and reloaded from the database,
      - the relation to Customer works as expected.
    """

    def setUp(self):
        # Minimal customer; adjust fields if your Customer model requires more.
        self.customer = Customer.objects.create(
            username="john.doe",
            first_name="John",
            last_name="Doe",
        )

    def test_create_and_reload_vehicle(self):
        """
        Create a vehicle, persist it, reload it, and verify fields/relations.
        """
        v = Vehicle.objects.create(
            owner=self.customer,
            license_plate="AA-11-BB",
            has_disability_permit=True,
        )

        # Reload from DB
        loaded = Vehicle.objects.get(pk=v.pk)

        self.assertEqual(loaded.owner.pk, self.customer.pk)
        self.assertEqual(loaded.license_plate, "AA-11-BB")
        self.assertTrue(loaded.has_disability_permit)


class VehicleServiceTests(TestCase):
    """
    Integration-like tests for VehicleService using the real ORM.

    This still counts as a unit test at the service level for this lab
    and demonstrates how the service wraps basic CRUD operations.
    """

    def setUp(self):
        self.customer = Customer.objects.create(
            username="alice",
            first_name="Alice",
            last_name="Smith",
        )
        self.service = VehicleService()

    def test_register_and_get_by_plate(self):
        """
        Service should register a vehicle and then find it by plate.
        """
        self.service.register_vehicle(
            owner=self.customer,
            license_plate="zz-99-yy",
            has_disability_permit=False,
        )

        # Lookup should be case-insensitive / normalized
        v = self.service.get_by_plate("ZZ-99-YY")

        self.assertIsNotNone(v)
        self.assertEqual(v.owner.pk, self.customer.pk)
        self.assertFalse(v.has_disability_permit)

    def test_get_by_owner(self):
        """
        Service should list all vehicles for a given owner.
        """
        self.service.register_vehicle(self.customer, "AA-00-AA")
        self.service.register_vehicle(self.customer, "BB-11-BB")

        vehicles = list(self.service.get_by_owner(self.customer))
        self.assertEqual(len(vehicles), 2)
