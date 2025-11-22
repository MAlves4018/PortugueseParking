from django.test import TestCase

import swd_django_demo


class TestDependencyContainer(TestCase):

    # this method is called before each test to set up the test environment
    # here we are getting the container from the swd_django_demo package
    def setUp(self):
        self.container = swd_django_demo.get_container()

    def test_customer_service(self):
        # fetch the CustomerService from the container
        customer_service = self.container.customer_service();
        # check that customer_service is not None
        self.assertIsNotNone(customer_service)

