import os

DB_NAME = 'c2g_jenkins_'
if os.environ.has_key('JOB_NAME'):
  DB_NAME += os.environ.get('JOB_NAME')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_NAME,                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'root',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SECRET_KEY = ''

# When PRODUCTION=True we don't show stackdumps on errors
PRODUCTION = False
INSTANCE = "jenkins"

# Put your name and email address here, so Django serious errors can come to you
ADMINS = (
        ('Class2Go Jenkins', 'c2g-dev@cs.stanford.edu')
        )

# Secrets used for S3 - Sef
AWS_ACCESS_KEY_ID = 'local'
AWS_SECRET_ACCESS_KEY = 'local'
AWS_STORAGE_BUCKET_NAME = 'local'

MEDIA_ROOT = '/var/lib/jenkins/test-data-sandbox/uploads'

PIAZZA_ENDPOINT = "https://piazza.com/basic_lti"
PIAZZA_KEY = "class2go.testing"
PIAZZA_SECRET = "piazza_secret_test"

# SMTP INFO for SES -- Amazon Simple Email Service $1 per 10K recipients
SES_SMTP_USER = ''
SES_SMTP_PASSWD = ''

# old credentials

# new credentials
YT_SERVICE_DEVELOPER_KEY = ''
GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''

GRADER_ENDPOINT='http://example.com/test'

