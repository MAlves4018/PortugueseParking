from dependency_injector import containers, providers

from customers.services import CustomerService
from parking.services import PricingService, PaymentService, SlotService
from contracts.services import TicketService
from vehicles.services import VehicleService
from core.event_coordinator import EventCoordinator

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    customer_service = providers.Factory(CustomerService)
    pricing_service = providers.Factory(PricingService)
    payment_service = providers.Factory(PaymentService)
    slot_service = providers.Factory(SlotService)
    vehicle_service = providers.Factory(VehicleService)
    ticket_service = providers.Factory(TicketService)

    event_coordinator = providers.Factory(
        EventCoordinator,
        ticket_service=ticket_service,
        slot_service=slot_service,
        pricing_service=pricing_service,
        payment_service=payment_service,
        vehicle_service=vehicle_service,
    )

container = Container()
