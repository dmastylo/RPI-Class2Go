# Shadow settings file that just overrides the DATABSE object
# so we can run the util machine with a local databse for the 
# job queue.

from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/sophi/celery/celerydb.sqlite',
    }
}

