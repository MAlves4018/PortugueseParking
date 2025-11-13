import threading

from django.db import transaction
from django.test import TransactionTestCase

from customers.models import Customer
from customers.services import CustomerService


# the django UnitTest would inherit from TransactionTestCase, but it does too much stuff resulting in database locks
class CustomerServiceConcurrencyTestCase(TransactionTestCase):
    def setUp(self):
        super().setUp()
        self._is_test_running = True
        with transaction.atomic():
            self.customer = Customer.objects.create(pk=1, credit=100)
            self.customer.save()

        self.customer_service = CustomerService()

    #MISSING TESTS
class Counter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1

    @property
    def value(self):
        with self._lock:
            return self._value
