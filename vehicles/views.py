from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render
from vehicles.services import VehicleService
from .models import Vehicle
from parking.models import SlotType


'''
 @login_required)
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(owner=request.user).select_related("minimum_slot_type")
    return render(request, "vehicles/vehicle_list.html", {"vehicles": vehicles})
'''

@login_required
def vehicle_list(request):
    service = VehicleService()
    vehicles = service.get_by_owner(request.user)
    return render(request, "vehicles/vehicle_list.html", {"vehicles": vehicles})

@login_required
def vehicle_create(request):
    slot_types = SlotType.objects.all().order_by("code")

    if request.method == "POST":
        plate = request.POST.get("license_plate", "").strip()
        slot_type_id = request.POST.get("minimum_slot_type") or None
        has_disability = bool(request.POST.get("has_disability_permit"))

        errors = []
        if not plate:
            errors.append("License plate is required.")

        if not errors:
            try:
                Vehicle.objects.create(
                    owner=request.user,
                    license_plate=plate.upper(),
                    minimum_slot_type_id=slot_type_id,
                    has_disability_permit=has_disability,
                )
                return redirect("vehicles:vehicle_list")
            except IntegrityError:
                errors.append("A vehicle with this plate already exists.")

        return render(
            request,
            "vehicles/vehicle_form.html",
            {"slot_types": slot_types, "errors": errors, "form_data": request.POST},
        )

    return render(
        request,
        "vehicles/vehicle_form.html",
        {"slot_types": slot_types, "errors": [], "form_data": {}},
    )
