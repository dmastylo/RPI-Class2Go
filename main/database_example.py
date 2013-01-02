# Don't forget to actually create the database named NAME
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'celery': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/class2go/celery/celerydb.sqlite',
    },

}

SECRET_KEY = ''

# Set PRODUCTION to True so we don't show stackdumps on errors
PRODUCTION = False
# Set this this to true if you want to show our maint page as root
MAINTENANCE_LANDING_PAGE = False

# The instance is the group of servers correspond to a C2G stack.  Some good 
# values for this are:
#    "your_name" if you want to stay isolated (thi is the default if missing)
#    "dev" to use the stable dev network util server
#    "stage" or "prod" for something in produciton -- are you sure you want to do that?
INSTANCE="dev"

# Put your name and email address here, so Django serious errors can come to you
# the trailing comma after the list is important so Python correctly interprets 
# this as a list of lists
ADMINS = (
        ('Class2Go Dev', "YOURNAME@stanford.edu"),
        )

# EMAIL ERROR PINGS
ERROR_SNIPPET_EMAILS = ['YOURNAME@stanford.edu',]


# For using S3 Storage, specify these with real settings
AWS_ACCESS_KEY_ID = 'AAAAAAAAAAAAAAAAAAAA'
AWS_SECRET_ACCESS_KEY = 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
AWS_STORAGE_BUCKET_NAME = 'dev-c2g'
AWS_SECURE_STORAGE_BUCKET_NAME = 'dev-secure-c2g' # Optional. If not defined here, it will be composed from the AWS_STORAGE_BUCKET_NAME in settings.py

# To use Local Storage.  You still need to define these three all to 'local'
# and specify where you want those local files written
# AWS_ACCESS_KEY_ID = 'local'
# AWS_SECRET_ACCESS_KEY = 'local'
# AWS_STORAGE_BUCKET_NAME = 'local'
# Celery must run for file uploads to work properly and video resizing to take place, etc.
# If you have the above values set to 'local', then set this value to True:
# CELERY_ALWAYS_EAGER = False
# AWS_SECURE_STORAGE_BUCKET_NAME = 'local'
# MEDIA_ROOT = '/opt/class2go/uploads'

# Celery must run for file uploads to work properly and video resizing to take place, etc.
# If you have the above values set to 'local', then set this value to True:
# CELERY_ALWAYS_EAGER = False

# Place where Kelvinator should do its work
# if not specified, then under /tmp, but on Amazon, want to use ephemeral storage
# which is /mnt for some reason
# Generally don't need to set this in dev
# KELVINATOR_WORKING_DIR = '/mnt'

# Place where we should spool uploads.  Django defaults to /tmp, which is fine on
# dev machines, but in AWS we want this to be on ephemeral storage
# FILE_UPLOAD_TEMP_DIR = '/mnt'

# This is if you want to change to a different logging directory than the default,
# which is '/var/log/django/'
# Please keep the trailing '/'
# LOGGING_DIR = '/my/logging/dir/'

PIAZZA_ENDPOINT = "https://piazza.com/basic_lti"
PIAZZA_KEY = "class2go"
PIAZZA_SECRET = "piazza_xxxxxxx"

# SMTP INFO for SES -- Amazon Simple Email Service $1 per 10K recipients
SES_SMTP_USER = "USER"
SES_SMTP_PASSWD = "PWD"

# class2go relies on Youtube pretty heavily. You need to have an API key 
# with youtube application integration enabled
YT_SERVICE_DEVELOPER_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
GOOGLE_CLIENT_ID = "NNNNNNNNNNNN.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "YYYYYYYYYYYYYYYYYYYYYYYY"

# Specify this if you want to hit this endpoint to do interactive grading. 
# If left blank, grading has a fallback "localhost" mode with dummy answers.
# GRADER_ENDPOINT = "nnnnnnnnnnnnnnnnnnnn.us-west-2.elb.amazonaws.com"
