"""
Data layer / repository abstractions for the parking domain.

All direct database access (Django ORM queries) is centralized here.
The service layer (SlotService, etc.) should only call these methods
and never perform queries on models directly.
"""

from django.db import transaction
from django.db.models import Q

from parking.models import ParkingSlot, ParkingArea
from contracts.models import Contract, Movement


class SlotRepository:
    """
    Repository responsible for reading ParkingSlot data from the database.
    """

    def __init__(self, queryset=None):
        # In production this will be ParkingSlot.objects
        self._qs = queryset or ParkingSlot.objects

    def get_candidates_for_vehicle(self, vehicle, area: ParkingArea | None = None):
        """
        Returns a queryset of candidate slots for a given vehicle and optional area.

        - Filters by area (if provided).
        - Applies a coarse filter by minimum slot type (e.g. size_rank) if available.
        Further compatibility checks (accessibility, etc.) can be done in the service
        or directly on the model (slot.is_compatible_with(vehicle)).
        """
        qs = self._qs.select_related("slot_type", "area")

        if area is not None:
            qs = qs.filter(area=area)

        required_type = getattr(vehicle, "minimum_slot_type", None)

        if required_type is not None and hasattr(required_type, "size_rank"):
            qs = qs.filter(slot_type__size_rank__gte=required_type.size_rank)

        return qs

    @transaction.atomic
    def lock_slot(self, slot_id):
        """
        Locks a single slot row for update, to be used in concurrent scenarios
        (e.g. final confirmation of a slot in UC1).
        """
        return self._qs.select_for_update().get(pk=slot_id)

    def get_slots_for_area(self, area: ParkingArea | None = None):
        """
        Returns all slots (optionally restricted to a given area).
        Used for occupancy statistics.
        """
        qs = self._qs.all()
        if area is not None:
            qs = qs.filter(area=area)
        return qs


class ContractRepository:
    """
    Repository for Contract (and subclasses) related queries.
    """

    def __init__(self, queryset=None):
        # In production this will be Contract.objects
        self._qs = queryset or Contract.objects

    def has_overlapping_for_slot(self, slot, start, end) -> bool:
        """
        Checks if there exists at least one contract on the given slot whose
        [valid_from, valid_to] interval overlaps [start, end].
        """
        return self._qs.filter(
            reserved_slot=slot,
            valid_from__lt=end,
            valid_to__gt=start,
        ).exists()


class MovementRepository:
    """
    Repository for Movement-related queries.
    """

    def __init__(self, queryset=None):
        # In production this will be Movement.objects
        self._qs = queryset or Movement.objects

    def count_occupied_slots_at(self, slots_qs, at) -> int:
        """
        Counts how many of the given slots are occupied at a specific time.

        A slot is considered occupied if:
        - it has at least one active contract at 'at'
        - that contract has an open movement (exit_time is NULL).
        """
        return slots_qs.filter(
            contracts__valid_from__lte=at,
            contracts__valid_to__gte=at,
            contracts__movements__exit_time__isnull=True,
        ).distinct().count()

    def get_movements_overlapping_period(self, start, end, area=None):
        """
        Returns movements whose [entry_time, exit_time] overlaps [start, end].
        Optionally filters by parking area.
        """
        qs = self._qs.filter(
            Q(entry_time__lt=end) & Q(exit_time__gt=start)
        )

        if area is not None:
            qs = qs.filter(contract__reserved_slot__area=area)

        return qs.select_related("contract")
