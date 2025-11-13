from unittest import TestCase
from unittest.mock import patch, Mock
from customers.services import CustomerService

"""
Please note, that we are inheriting from TestCase form the unittest module and not from django.test.TestCase.
This is because we are not testing any Django specific functionality, but only the service class.
"""


class TestCustomerService(TestCase):
    """
    The setUp method is a special method in the TestCase class of the unittest module that is called
    before each test method in the test case.
    Its purpose is to set up any resources or objects that the test methods will need.
    """

    def setUp(self):
        # create a mock instance of the Customer model
        self.mock_instance = Mock()
        # create a CustomerService instance
        self.customer_service: CustomerService = CustomerService()

    #MISSING TESTS