import threading

from django.utils.functional import wraps
from django.conf import settings

threadlocal = threading.local()

class database_guard_context_manager():
    def __enter__(self):
        if 'readonly' in settings.DATABASES:
            threadlocal.DATABASE_OVERRIDE = 'readonly' 
    def __exit__(self, exc_type, exc_val, exc_tb):
        threadlocal.DATABASE_OVERRIDE = None

def use_readonly_database(wrapped_view):
    """A decorator that sets a thread-local variable so that subsequent
    database calls will use the readonly database.

    Got the idea from http://python.dzone.com/articles/django-switching-databases
    """
    @wraps(wrapped_view)
    def inner(*args, **kwargs):
        with database_guard_context_manager():
            return wrapped_view(*args, **kwargs)
    return inner

def get_database_considering_override():
    return getattr(threadlocal, 'DATABASE_OVERRIDE', 'default')

