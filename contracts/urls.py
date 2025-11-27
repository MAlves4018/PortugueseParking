from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path("season/new/", views.season_ticket_new, name="season_ticket_new"),
    path("season/", views.season_ticket_list, name="season_ticket_list"),
    path("gate-entry/", views.gate_entry, name="gate_entry"),
    path("gate-exit/", views.gate_exit, name="gate_exit"),
]
