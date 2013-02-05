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
        'NAME': 'celerydb.sqlite',
    },

}

SECRET_KEY = ''

# Set PRODUCTION to True so we don't show stackdumps on errors
PRODUCTION = False
# Set this this to true if you want to show our maint page as root
MAINTENANCE_LANDING_PAGE = False

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))

LOGGING_DIR = os.path.join(PROJECT_ROOT, "logs")
LOCAL_CACHE_LOCATION = os.path.join(PROJECT_ROOT, "cache-default")
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")

# The instance is the group of servers correspond to a C2G stack.  Some good 
# values for this are:
#    "your_name" if you want to stay isolated (thi is the default if missing)
#    "dev" to use the stable dev network util server
#    "stage" or "prod" for something in produciton -- are you sure you want to do that?
INSTANCE="dev"

# Information about this site. Note that the short name here is used to
# build paths to site assets, so is specific and case-sensitive.
SITE_ID = 1
SITE_NAME_SHORT = 'Stanford'
SITE_NAME_LONG = 'Stanford University'
SITE_TITLE = 'Stanford Class2Go'

# Put your name and email address here, so Django serious errors can come to you
# the trailing comma after the list is important so Python correctly interprets 
# this as a list of lists
ADMINS = (
        ('Class2Go Dev', "YOURNAME@stanford.edu"),
        )

# EMAIL ERROR PINGS
ERROR_SNIPPET_EMAILS = ['YOURNAME@stanford.edu',]

#########
# S3 Storage configuration. Read both stanzas so you understand what these do.
#########
# For using S3 Storage, specify these with real settings. The ACCESS virables
# are used for authorization to S3 and should be kept secret.
AWS_ACCESS_KEY_ID = 'AAAAAAAAAAAAAAAAAAAA'
AWS_SECRET_ACCESS_KEY = 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
##
# There are three buckets: STORAGE, SECURE_STORAGE, and RELEASE. STORAGE is
# used for storing public assets and instructor-uploaded material, such as
# downloadable files. SECURE_STORAGE should be configured with a more limited
# set of permissions (allowing download by instructors and not the general
# public), and is used for distributing things like student performance
# reports. RELEASE should be configured with the most limited set of
# permissions, only allowing dowload only from your production (and optionally
# developer) credentials. It is used for the distribution of materials used in
# release and deployment, like custom binaries, secondary authorization tokens,
# etc.
AWS_STORAGE_BUCKET_NAME = 'my-dev-bucket'
AWS_SECURE_STORAGE_BUCKET_NAME = 'my-secure-dev-bucket'
AWS_RELEASE_BUCKET_NAME = 'my-release-dev-bucket'
# For using Local btorage, set all of these variables to 'local'. You also
# must specify where you want files locally written (see MEDIA_ROOT, below)
##
# AWS_ACCESS_KEY_ID = 'local'
# AWS_SECRET_ACCESS_KEY = 'local'
# AWS_STORAGE_BUCKET_NAME = 'local'
# AWS_SECURE_STORAGE_BUCKET_NAME = 'local'
# AWS_RELEASE_BUCKET_NAME = 'local'
# MEDIA_ROOT = '/opt/class2go/uploads'

#########
# Celery configuration
#########
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
