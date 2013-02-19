import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'class2go',                     
        'USER': 'root',                     
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SECRET_KEY = ''

# When PRODUCTION=True we don't show stackdumps on errors
PRODUCTION = False
INSTANCE = "travis"

# Put your name and email address here, so Django serious errors can come to you
ADMINS = (
        ('Class2Go Travis', 'class2go-dev@stanford.edu')
        )

AWS_ACCESS_KEY_ID = 'local'
AWS_SECRET_ACCESS_KEY = 'local'
AWS_STORAGE_BUCKET_NAME = 'local'

MEDIA_ROOT =           '/tmp/storage'
LOGGING_DIR =          '/tmp/logs'
STATIC_ROOT =          '/tmp/static'
LOCAL_CACHE_LOCATION = '/tmp/cache'

PIAZZA_ENDPOINT = "https://piazza.com/basic_lti"
PIAZZA_KEY = "class2go.testing"
PIAZZA_SECRET = "piazza_secret_test"

SES_SMTP_USER = ''
SES_SMTP_PASSWD = ''

YT_SERVICE_DEVELOPER_KEY = ''
GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''

GRADER_ENDPOINT='http://example.com/test'

