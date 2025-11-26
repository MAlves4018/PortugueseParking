from django.contrib.auth.models import AbstractUser
from django.db import models

from customers.managers import CustomerManager


"""
We are using the Customer model for authentication, so it must be based on AbstractUser.
For this project, only add nullable/optional fields to avoid issues when creating superusers.
"""


class CustomerBase(AbstractUser):
    """
    Base customer model, swappable and mapped to its own DB table.
    """

    # Use a manager that inherits from django.contrib.auth.models.UserManager
    objects: CustomerManager = CustomerManager()

    class Meta:
        # Allows swapping this model via settings.CUSTOMER_MODEL if needed
        swappable: str = "CUSTOMER_MODEL"
        db_table: str = "customer_base"

    def __str__(self) -> str:
        return self.username


class Customer(CustomerBase):
    """
    Concrete customer model used in the project.
    Extends CustomerBase with extra domain fields.
    """

    ssn = models.CharField(
        max_length=50,
        blank=True,
        help_text="SSN or equivalent identifier.",
    )

    billing_info = models.TextField(
        blank=True,
        help_text="Optional billing information.",
    )

    credit = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional customer credit balance.",
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

    class Meta:
        db_table: str = "customer_concrete"
