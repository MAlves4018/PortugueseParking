# The init.py file is used to initialize a Python package.

import _thread
import threading
from django.apps import apps
from swd_django_demo import settings

# this is going to be our container for dependency injection
container = None


# retrieve the container
def get_container():
    return container


# Defining a function to wait for a ready event (when all apps are loaded)
# and then create the container containing the dependencies and wire it.
# This is done in a separate thread to avoid blocking the main thread.

def wait_for_ready_event(ready_event: threading.Event) -> None:
    global container
    print('wait_for_event starting')
    event_is_set = ready_event.wait()

    print('event set: %s', event_is_set)
    try:
        # we would run into issues if we import Container before the apps are ready
        from swd_django_demo.containers import Container
        container = Container()  # <-- create the container here
        # settings.__dict__ returns a dictionary containing all the variables defined in the settings module.
        # The from_dict() method of the config provider of the Container class takes a dictionary as an argument
        # and sets the configuration of the container with the key-value pairs in the dictionary.
        container.config.from_dict(settings.__dict__)
        # The wire() method of the container class takes a list of modules as an argument and wires the modules
        # with the container. This means that the container will inject the dependencies into the modules
        # allowing them to use the dependencies that they need without having to manually create them.
        container.wire(modules=["orders.views",
                                "core.dtos", ])

    except Exception as e:
        print("Exception occurred during dependency injection: ", e)
        _thread.interrupt_main()


# Creating a thread to wait for the app ready event
t1 = threading.Thread(name='delayed_app_ready',
                      target=wait_for_ready_event,
                      args=(apps.ready_event,))
t1.start()
