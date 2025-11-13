import time
from typing import Optional

from django.db import models, transaction

from core.dtos import CustomerDTO
from core.services import ICustomerService
from customers.models import Customer


class CustomerService(ICustomerService):
    """
        Implementation of the ICustomerService interface for checking if a customer has any credit or not.
    """
    def __init__(self, repo=None):
        # default to Product.objects, but allow tests to pass a fake
        self.repo = repo or Customer.objects

    def get_by_id(self, id: str) -> Optional[Customer]:
        return self.repo.get_by_id(id=id)

    def get_dto_by_id(self, id: str) -> Optional[CustomerDTO]:
        customer:Customer = self.get_by_id(id=id)
        if customer:
            return CustomerDTO(id=customer.id, username=customer.username, email=customer.email,
                               first_name=customer.first_name, last_name=customer.last_name)
        return None

    def get_by_username(self, username: str) -> Optional[Customer]:
        return self.repo.get_by_username(username=username)

    def get_dto_by_username(self, username: str) -> Optional[CustomerDTO]:
        customer:Customer = self.get_by_username(username=username)
        if customer:
            return CustomerDTO(id=customer.id, username=customer.username, email=customer.email, first_name=customer.first_name,
                                last_name=customer.last_name)
        return None
