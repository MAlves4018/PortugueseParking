# vehicles/services.py

from typing import Iterable, Optional

from django.conf import settings
from django.apps import apps
from django.db import models

from customers.models import Customer
from parking.models import SlotType

class VehicleService:
    """
    Service for vehicle-related operations.

    This service encapsulates the persistence logic for Vehicle entities:
      - register new vehicles,
      - lookup by license plate,
      - list vehicles per customer.

    It uses the Django ORM by default but can be replaced by mocks
    in unit tests if needed. The concrete Vehicle model is swappable
    via settings.VEHICLE_MODEL.
    """

    def __init__(self, vehicle_repo: Optional[models.Manager] = None) -> None:
        """
        Constructor with an optional repository abstraction.

        By default, we use Vehicle.objects (Django ORM manager).
        In tests, we may inject a fake or mocked repository.
        """
        if vehicle_repo is not None:
            self._vehicle_repo = vehicle_repo
        else:
            vehicle_model = apps.get_model(settings.VEHICLE_MODEL)
            self._vehicle_repo = vehicle_model.objects

    # --------------------------------------------------
    # Registration / CRUD
    # --------------------------------------------------
    def register_vehicle(self, owner: Customer, license_plate: str, minimum_slot_type: Optional[SlotType] = None, has_disability_permit: bool = False):
        """
        Register a new vehicle for a customer.

        This method:
          - normalizes the license plate (upper-cased),
          - creates and persists the Vehicle entity.
        """
        normalized_plate = license_plate.strip().upper()

        return self._vehicle_repo.create(
            owner=owner,
            license_plate=normalized_plate,
            minimum_slot_type=minimum_slot_type,
            has_disability_permit=has_disability_permit,
        )

    # --------------------------------------------------
    # Queries
    # --------------------------------------------------
    def get_by_plate(self, license_plate: str):
        """
        Find a vehicle by its license plate.

        Returns:
          - Vehicle instance if found,
          - None otherwise.
        """
        normalized_plate = license_plate.strip().upper()

        try:
            return self._vehicle_repo.get(license_plate=normalized_plate)
        except self._vehicle_repo.model.DoesNotExist:
            return None

    def get_by_owner(self, owner: Customer) -> Iterable:
        """
        List all vehicles belonging to a given customer.
        """
        return self._vehicle_repo.filter(owner=owner)

    # --------------------------------------------------
    # Flags / updates
    # --------------------------------------------------
    def set_minimum_slot_type(self, vehicle, slot_type: Optional[SlotType]):
        """
        Update the minimum slot type that this vehicle requires.
        """
        vehicle.minimum_slot_type = slot_type
        vehicle.save(update_fields=["minimum_slot_type"])
        return vehicle

    def set_disability_permit(self, vehicle, has_permit: bool = True):
        """
        Update the 'has_disability_permit' flag of a given vehicle.
        """
        vehicle.has_disability_permit = has_permit
        vehicle.save(update_fields=["has_disability_permit"])
        return vehicle
