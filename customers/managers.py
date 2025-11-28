from django.contrib.auth.models import UserManager


class CustomerManager(UserManager):
    """
    Custom manager for Customer models.

    Extends Django's UserManager, so that methods like
    create_user() e create_superuser() funcionam corretamente.
    Não importa o modelo Customer para evitar imports circulares.
    """
    pass
