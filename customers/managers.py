from typing import Optional

from django.contrib.auth.base_user import BaseUserManager

from customers.models import Customer

class CustomerManager(BaseUserManager):
    def get_by_id(self, id: int) -> Optional[Customer]:
        return self.get_queryset().filter(pk=id).first()

    def get_by_username(self, username: str) -> Optional[Customer]:
        return self.get_queryset().filter(username=username).first()
