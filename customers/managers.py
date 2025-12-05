from django.contrib.auth.models import UserManager


class CustomerManager(UserManager):
    """
    Custom manager for Customer models.

    Extends Django's UserManager so that methods such as
    create_user() and create_superuser() work correctly.
    The Customer model is not imported here to avoid circular imports.
    """
    pass
