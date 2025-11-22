"""
This file defines the project's dependency injection container.
"""

from dependency_injector import containers, providers

# --- parking / tickets domain services ---
from parking.services import PricingService, PaymentService
from contracts.services import TicketService


class Container(containers.DeclarativeContainer):
    """Main DI container for the project."""

    # Configuration provider (if you want to read settings later)
    config = providers.Configuration()

    # Parking pricing service
    pricing_service = providers.Factory(
        PricingService,
    )

    # Mocked payment service
    payment_service = providers.Factory(
        PaymentService,
    )

    # Ticket service, wired with pricing + payment
    ticket_service = providers.Factory(
        TicketService,
        pricing_service=pricing_service,
        payment_service=payment_service,
    )

# Global container instance (used by swd_django_demo.__init__.py)
container = Container()
