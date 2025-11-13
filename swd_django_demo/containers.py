"""
This file defines the project's dependency injection container.
It wires both the demo services (ProductService, CustomerService, OrderService)
and the newly added parking/ticketing services (PricingService, PaymentService, TicketService).

The container defines:
 - configuration provider,
 - singleton providers for existing services,
 - factory providers where appropriate,
 - providers for pricing/payment/ticket services with proper dependency injection,
 - wiring configuration for dependency resolution inside Django apps.
"""

from dependency_injector import containers, providers

# --- demo project services (from base template) ---
from products.services import ProductService
from customers.services import CustomerService
from orders.services import OrderService
from products.models import Product
from contracts.services import TicketService
from parking.services import PricingService, PaymentService

# --- new domain services (your parking/tickets implementation) ---
class Container(containers.DeclarativeContainer):
    """Main DI container for the project."""
    # ---------------------------------------------------------------
    # Base project services (from template)
    # ---------------------------------------------------------------

    # Configuration provider
    config = providers.Configuration()

    # Singleton provider for ProductService
    product_service = providers.Singleton(
        ProductService,
    )

    # Singleton provider for CustomerService
    customer_service = providers.Singleton(
        CustomerService,
    )

    # Factory provider that creates Product instances
    product_factory = providers.Factory(
        Product,
        id=int,
        name=str,
        description=str
    )

    # Singleton provider for OrderService (depends on ProductService + CustomerService)
    order_service = providers.Singleton(
        OrderService,
        product_service=product_service,
        customer_service=customer_service,
    )

    # ---------------------------------------------------------------
    # New services for the parking/ticket domain
    # ---------------------------------------------------------------

    # Pricing service provider
    pricing_service = providers.Factory(
        PricingService,
    )

    # Payment service provider (mock implementation)
    payment_service = providers.Factory(
        PaymentService,
    )

    # Ticket service with dependency injection of pricing and payment
    ticket_service = providers.Factory(
        TicketService,
        pricing_service=pricing_service,
        payment_service=payment_service,
    )


# Global container instance (imported by the project)
container = Container()

