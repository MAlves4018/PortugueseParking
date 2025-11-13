# vehicles/services.py

from typing import Iterable, Optional

from django.db import models

from customers.models import Customer
from .models import Vehicle


class VehicleService:
    """
    Service for vehicle-related operations.

    This service encapsulates the persistence logic for Vehicle entities:
      - register new vehicles,
      - lookup by license plate,
      - list vehicles per customer.

    It uses the Django ORM by default but can be replaced by mocks
    in unit tests if needed.
    """

    def __init__(self, vehicle_repo: Optional[models.Manager] = None) -> None:
        """
        Constructor with an optional repository abstraction.

        By default, we use Vehicle.objects (Django ORM manager).
        In tests, we may inject a fake or mocked repository.
        """
        self._vehicle_repo = vehicle_repo or Vehicle.objects

    # --------------------------------------------------
    # Registration / CRUD
    # --------------------------------------------------
    def register_vehicle(
        self,
        owner: Customer,
        license_plate: str,
        is_oversize: bool = False,
        has_disability_permit: bool = False,
    ) -> Vehicle:
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
            is_oversize=is_oversize,
            has_disability_permit=has_disability_permit,
        )

    # --------------------------------------------------
    # Queries
    # --------------------------------------------------
    def get_by_plate(self, license_plate: str) -> Optional[Vehicle]:
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

    def get_by_owner(self, owner: Customer) -> Iterable[Vehicle]:
        """
        List all vehicles belonging to a given customer.
        """
        return self._vehicle_repo.filter(owner=owner)

    # --------------------------------------------------
    # Flags / updates
    # --------------------------------------------------
    def mark_oversize(self, vehicle: Vehicle, is_oversize: bool = True) -> Vehicle:
        """
        Update the 'is_oversize' flag of a given vehicle.
        """
        vehicle.is_oversize = is_oversize
        vehicle.save(update_fields=["is_oversize"])
        return vehicle

    def set_disability_permit(
        self, vehicle: Vehicle, has_permit: bool = True
    ) -> Vehicle:
        """
        Update the 'has_disability_permit' flag of a given vehicle.
        """
        vehicle.has_disability_permit = has_permit
        vehicle.save(update_fields=["has_disability_permit"])
        return vehicle
