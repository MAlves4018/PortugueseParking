from django.urls import path
from . import views

app_name = "vehicles"

urlpatterns = [
    path("", views.vehicle_list, name="vehicle_list"),
    path("new/", views.vehicle_create, name="vehicle_create"),
]
