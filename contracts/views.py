from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from contracts.models import RegularContract, OccasionalTicket
from vehicles.models import Vehicle
from parking.models import ParkingSlot, Gate
from .models import RegularContract
from .services import TicketService
from parking.services import PricingService, PaymentService

from django.db.models import Exists, OuterRef
import logging

logger = logging.getLogger(__name__)


def _get_available_slots_for(vehicle, valid_from, valid_to):
    """
    Returns the list of ParkingSlot objects that are available for this
    vehicle and time period:

    - without overlapping regular contracts
    - compatible with the vehicle’s required slot type (minimum slot type)
    - respecting accessibility rules:
        * vehicles with a disability permit only see accessible slots
        * vehicles without a disability permit do not see accessible slots
    """
    overlapping_contracts = RegularContract.objects.filter(
        reserved_slot=OuterRef("pk"),
        valid_from__lt=valid_to,
        valid_to__gt=valid_from,
    )

    qs = ParkingSlot.objects.select_related("slot_type", "area").annotate(
        has_overlap=Exists(overlapping_contracts)
    ).filter(has_overlap=False)

    has_disability = getattr(vehicle, "has_disability_permit", False)

    if has_disability:
        qs = qs.filter(is_accessible=True)
    else:
        qs = qs.filter(is_accessible=False)

    compatible_slots = [slot for slot in qs if vehicle.can_use_slot(slot)]

    return compatible_slots

def _build_ticket_service():
    pricing = PricingService()
    payment = PaymentService()
    return TicketService(
        pricing_service=pricing,
        payment_service=payment,
    )


@login_required
def season_ticket_new(request):
    """
    Simple UI for UC1:
      - user selects vehicle, slot, period
      - delegates to TicketService.purchase_season_ticket
    """
    service = _build_ticket_service()
    vehicles = Vehicle.objects.filter(owner=request.user)

    slots = ParkingSlot.objects.select_related("slot_type", "area").order_by(
        "area__name", "number"
    )

    errors = []
    form_data = {}
    price = None
    preview_mode = False

    if request.method == "POST":
        action = request.POST.get("action", "preview")

        vehicle_id = request.POST.get("vehicle_id")
        slot_id = request.POST.get("slot_id") or None
        valid_from_raw = request.POST.get("valid_from")
        valid_to_raw = request.POST.get("valid_to")

        form_data = request.POST.copy()

        if action != "cancel":
            if not vehicle_id:
                errors.append("You must select a vehicle.")
            if not valid_from_raw or not valid_to_raw:
                errors.append("You must provide a start and end date.")

        vf = vt = None
        vehicle = None

        if not errors and action != "cancel":
            vf = parse_datetime(valid_from_raw)
            vt = parse_datetime(valid_to_raw)
            if not vf or not vt or vf >= vt:
                errors.append("Invalid period.")
            else:
                try:
                    vehicle = Vehicle.objects.get(pk=vehicle_id, owner=request.user)
                except Vehicle.DoesNotExist:
                    errors.append("Invalid vehicle selected.")

        if not errors and vehicle is not None:
            slots = _get_available_slots_for(vehicle, vf, vt)

        if action == "cancel":
            cancel_reason = request.POST.get("cancel_reason", "").strip()
            if not cancel_reason:
                errors.append("Please tell us why you cancelled the order.")
            else:
                logger.info(
                    "Season ticket order cancelled by user %s. Reason: %s",
                    request.user.id,
                    cancel_reason,
                )
                return redirect("contracts:season_ticket_list")

        elif action == "preview" and not errors:
            if not slot_id:
                errors.append("You must select a parking slot to see the price.")
            else:
                if not any(str(s.id) == str(slot_id) for s in slots):
                    errors.append(
                        "Selected slot is no longer available for that period. "
                        "Please choose another one."
                    )
                else:
                    pricing = PricingService()
                    price = pricing.get_season_price(
                        slot_id=slot_id,
                        period=(vf, vt),
                    )
                    preview_mode = True

        elif action == "confirm" and not errors:
            if not slot_id:
                errors.append("You must select a parking slot.")
            else:
                vehicle = Vehicle.objects.get(pk=vehicle_id)
                result = service.purchase_season_ticket(
                    customer_id=request.user.id,
                    vehicle_plate=vehicle.license_plate,
                    slot_id=slot_id,
                    valid_from=vf,
                    valid_to=vt,
                )
                if result.get("success"):
                    return redirect("contracts:season_ticket_list")
                else:
                    errors.append(result.get("reason", "Unknown error."))

        context = {
            "vehicles": vehicles,
            "slots": slots,
            "errors": errors,
            "form_data": form_data,
            "price": price,
            "preview_mode": preview_mode,
        }
        return render(request, "contracts/season_ticket_form.html", context)

    context = {
        "vehicles": vehicles,
        "slots": slots,
        "errors": errors,
        "form_data": form_data,
        "price": price,
        "preview_mode": False,
    }
    return render(request, "contracts/season_ticket_form.html", context)


@login_required
def season_ticket_list(request):
    contracts = RegularContract.objects.filter(customer=request.user).select_related(
        "vehicle", "reserved_slot", "reserved_slot__area"
    )
    return render(
        request,
        "contracts/season_ticket_list.html",
        {"contracts": contracts},
    )


@login_required
def gate_entry(request):
    """
    Simple form to simulate UC2:
      - user types license plate and gate
      - we call TicketService.enter_with_season_ticket
    """
    service = _build_ticket_service()
    result = None

    if request.method == "POST":
        plate = request.POST.get("license_plate", "").strip()
        gate_id = request.POST.get("gate_id")
        if plate and gate_id:
            result = service.enter_with_season_ticket(plate.upper(), gate_id)

    gates = Gate.objects.select_related("area").all()
    return render(
        request,
        "contracts/gate_entry.html",
        {"gates": gates, "result": result},
    )

@login_required
def gate_exit(request):
    """
    Simple form to simulate exiting with a season ticket:

      - user types license plate and gate
      - we call TicketService.exit_with_season_ticket
    """
    service = _build_ticket_service()
    result = None

    if request.method == "POST":
        plate = request.POST.get("license_plate", "").strip()
        gate_id = request.POST.get("gate_id")
        if plate and gate_id:
            result = service.exit_with_season_ticket(plate.upper(), gate_id)

    gates = Gate.objects.select_related("area").all()
    return render(
        request,
        "contracts/gate_exit.html",
        {"gates": gates, "result": result},
    )

@login_required
def gate_occasional_entry(request):
    """
    Simulate occasional customer entry: create a single-use ticket.
    """
    service = _build_ticket_service()
    result = None

    if request.method == "POST":
        plate = request.POST.get("license_plate", "").strip()
        gate_id = request.POST.get("gate_id")
        if plate and gate_id:
            result = service.start_occasional_entry(plate, gate_id)

    gates = Gate.objects.select_related("area").all()
    return render(
        request,
        "contracts/gate_occasional_entry.html",
        {"gates": gates, "result": result},
    )

@login_required
def occasional_cash_device(request):
    """
    Simulate payment terminal for occasional customers.
    """
    service = _build_ticket_service()
    pricing = None
    payment_result = None

    if request.method == "POST":
        action = request.POST.get("action")
        plate = request.POST.get("license_plate", "").strip()

        if plate:
            if action == "calculate":
                pricing = service.get_occasional_pricing(plate)
            elif action == "pay":
                payment_result = service.pay_occasional_ticket(plate)

    return render(
        request,
        "contracts/occasional_cash_device.html",
        {"pricing": pricing, "payment_result": payment_result},
    )

@login_required
def gate_occasional_exit(request):
    """
    Simulate exit gate for occasional customers.
    """
    service = _build_ticket_service()
    result = None

    if request.method == "POST":
        plate = request.POST.get("license_plate", "").strip()
        gate_id = request.POST.get("gate_id")
        if plate and gate_id:
            result = service.exit_with_occasional_ticket(plate, gate_id)

    gates = Gate.objects.select_related("area").all()
    return render(
        request,
        "contracts/gate_occasional_exit.html",
        {"gates": gates, "result": result},
    )