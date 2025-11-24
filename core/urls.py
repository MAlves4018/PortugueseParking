from django.urls import path

from . import views

app_name = "core"

# Map URLs to views
urlpatterns = [
    # Map the index URL of the "core" application to the index view
    path("health", views.health_check, name="health_check"),
    path('', views.home, name='home')
]
