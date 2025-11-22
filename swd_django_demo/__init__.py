# The init.py file is used to initialize a Python package.

import _thread
import threading
from django.apps import apps
from swd_django_demo import settings

# this is going to be our container for dependency injection
container = None


def get_container():
    return container


def wait_for_ready_event(ready_event: threading.Event) -> None:
    global container
    print('wait_for_event starting')
    event_is_set = ready_event.wait()
    print('event set: %s', event_is_set)
    try:
        from swd_django_demo.containers import Container
        container = Container()
        container.config.from_dict(settings.__dict__)
        container.wire(modules=["core.dtos", ])
    except Exception as e:
        print("Exception occurred during dependency injection: ", e)
        _thread.interrupt_main()


t1 = threading.Thread(
    name='delayed_app_ready',
    target=wait_for_ready_event,
    args=(apps.ready_event,),
)
t1.start()
