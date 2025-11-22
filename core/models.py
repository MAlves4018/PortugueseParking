from django.contrib.auth.models import AbstractUser

"""
In Django, the AbstractUser class is a built-in model class that provides a starting point for creating a
custom user model. It is designed to be subclassed by users who wish to implement their own custom user model while 
retaining some of the core functionality of the built-in Django User model.
By inheriting from AbstractUser, the Customer model class is able to inherit the fields and methods 
of the AbstractUser class, which includes built-in user authentication and authorization features, 
such as the ability to log in, log out, and set a password. 
This allows developers to easily customize the user model to fit their specific needs while still retaining 
the core functionality of the built-in user model.
"""


class Customer(AbstractUser):
    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.username
