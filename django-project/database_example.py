DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SECRET_KEY = ''

# Set PRODUCTION to True so we don't show stackdumps on errors
PRODUCTION = False

# Put your name and email address here, so Django serious errors can come to you
ADMINS = (
        ('Class2Go Dev', "YOURNAME@stanford.edu")
        )

# For using S3 Storage, specify these with real settings
AWS_ACCESS_KEY_ID = 'AAAAAAAAAAAAAAAAAAAA'
AWS_SECRET_ACCESS_KEY = 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
AWS_STORAGE_BUCKET_NAME = 'dev-c2g'

# To use Local Storage.  You still need to define these three all to 'local'
# and specify where you want those local files written
# AWS_ACCESS_KEY_ID = 'local'
# AWS_SECRET_ACCESS_KEY = 'local'
# AWS_STORAGE_BUCKET_NAME = 'local'
# MEDIA_ROOT = '/opt/class2go/uploads'

