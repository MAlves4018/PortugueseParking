# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import Customer
from customers.managers import CustomerManager

"""
    we are using the Customer model for authentication, so we need to use the AbstractUser model
    for this project, only add nullable fields to the customer,
    otherwise you could run into trouble with creating suerpusers.
    
"""


class CustomerBase(Customer):
    objects: CustomerManager = CustomerManager()
    class Meta:
        # swappable is used to swap out the default user model with our custom user model
        swappable: str = "CUSTOMER_MODEL"
        db_table: str = "customer_base"


# this is the concrete model that we will use for the project
class Customer(CustomerBase):
    ssn = models.CharField(max_length=50, blank=True)  # SSN or equivalent
    billing_info = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

    class Meta:
        db_table: str = "customer_concrete"
    # we are adding a credit field to the customer model
    credit: float = models.FloatField(null=True)
