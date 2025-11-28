# parking/urls.py
from django.urls import path
from . import views

app_name = "parking"

urlpatterns = [
    path("stats/", views.stats_overview, name="stats_overview"),
]
