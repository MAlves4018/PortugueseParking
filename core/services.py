from abc import ABC, abstractmethod
from typing import List, Optional

from django.db import models

from core.dtos import CustomerDTO
from core.models import Customer

"""
In this code, we are defining the interfaces for the services.
Interfaces are abstract classes that declare a set of methods that must be implemented
by any concrete class that implements the interface.
"""

# ==========================================
# Existing interfaces (demo / base project)
# ==========================================

class ICustomerService(ABC):
    """
    Interface for customer-related operations.
    Part of the base demo project.
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Customer]:
        """Return a Customer instance by ID."""
        pass

    @abstractmethod
    def get_dto_by_id(self, id: int) -> Optional[CustomerDTO]:
        """Return a customer DTO for the given ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Customer]:
        """Return a customer by username."""
        pass



# ==========================================
# New interfaces (parking / tickets domain)
# ==========================================


class ITicketService(ABC):
    """
    Service for ticket-related operations (season tickets, gate entry, etc.).
    For now, we keep the signatures untyped because the ticket models are
    not fully defined yet.
    """

    @abstractmethod
    def purchase_season_ticket(self, customer_id, slot_id, license_plate):
        """
        UC1: purchase a season ticket for a given customer, slot and license plate.
        Should:
          - calculate the correct price (using a pricing service),
          - perform a payment (using a payment service),
          - create and persist the season ticket.
        """
        pass

    @abstractmethod
    def enter_with_season_ticket(self, license_plate, gate_id):
        """
        UC2: handle entry at a gate using a license plate.
        Should:
          - validate that there is a valid season ticket for the plate,
          - ensure it is not already 'in use',
          - register the entry movement,
          - return a result that tells the gate whether to open or not.
        """
        pass


class IPricingService(ABC):
    """
    Service for computing prices.
    Supports:
    - Season ticket pricing (UC1)
    - Occasional parking pricing (future optional UC)
    """

    @abstractmethod
    def get_season_price(self, slot_id, period):
        """
        Compute the price for a season ticket.
        Arguments:
        - slot_id: ID of the parking slot
        - period: period tuple (valid_from, valid_to)
        """
        pass

    @abstractmethod
    def get_occasional_price(self, slot_id, duration_minutes: int):
        """
        Compute the price for occasional parking.
        Arguments:
        - slot_id: ID of the parking slot
        - duration_minutes: duration of stay in minutes
        """
        pass



class IPaymentService(ABC):
    """
    Service for processing payments.
    In this project, the payment system is mocked.
    """

    @abstractmethod
    def process_payment(self, customer_id, amount):
        """
        Process a payment for a given customer and amount.
        Should return True on success or False on failure.
        """
        pass


class ITicketService(ABC):
    """
    Service interface for ticket-related operations.
    UC1: Purchase a season ticket
    UC2: Entry with season ticket
    """

    @abstractmethod
    def purchase_season_ticket(
        self,
        customer_id,
        vehicle_plate,
        slot_id,
        valid_from,
        valid_to,
    ):
        """
        UC1: Purchase a season ticket.

        - Validates that the customer and vehicle exist.
        - Validates that the selected slot is available for the whole period.
        - Calculates the price using the pricing service.
        - Processes the payment using the payment service.
        - Creates a regular contract and reserves the slot.
        - Returns a DTO or simple dict with the result.
        """
        pass

    @abstractmethod
    def enter_with_season_ticket(
        self,
        license_plate,
        gate_id,
    ):
        """
        UC2: Entry with season ticket.

        - Finds a valid season ticket (regular contract) for the license plate.
        - Checks that the ticket is not already 'in use' (no open movement).
        - Records a movement (entry) with timestamp and gate.
        - Returns a result telling if the gate should open and why.
        """
        pass

AbstractTicketService = ITicketService
AbstractPricingService = IPricingService
AbstractPaymentService = IPaymentService