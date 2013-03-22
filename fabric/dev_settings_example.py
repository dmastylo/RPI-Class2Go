

EC2_REGION = "ap-southeast-2"
EC2_AMI = "ami-e2ba2cd8"
EC2_SECURITY = "prod"
EC2_INSTANCE_TYPE = "m1.small"
EC2_KEY_PAIR = "KeyPair"
EC2_TAG = "app2.dev"
EC2_ELB = "UWAC2GDev"

# "c2g_fab_web" => {
# AWS GLOBAL
AWS_ACCESS_KEY_ID = 'ABCDEFGHIJK'
AWS_SECRET_ACCESS_KEY = 'abcsklsdfjasjf+sdf+asfsd'


# RDS - Main Database
DATABASE_HOST = "env.cccccccccccc.us-west-2.rds.amazonaws.com"
DATABASE_INSTANCE = "class2go"
DATABASE_USER = "xxxxxxxxxxxx"
DATABASE_PASSWORD = "dddddddddd"

# RDS - Readonly Database Instance

READONLY_DATABASE_HOST = "env.cccccccccccc.us-west-2.rds.amazonaws.com"
READONLY_DATABASE_INSTANCE = "class2go"
READONLY_DATABASE_USER = "xxxxxxxxxxxx"
READONLY_DATABASE_PASSWORD = "dddddddddd"


# s3 - storage buckets
STORAGE_BUCKET = "stage-c2g"         # class assets
SECURE_BUCKET = "stage-c2g"          # reports
RELEASE_BUCKET = "qqqqqqqqqqqqqqqq",  # private info

# ses - bulk email service
SMTP_USER = "eeeeeeeeeeeeeeeeeeee"
SMTP_PASSWORD = "ffffffffffffffffffffffffffffffffffffffffffff"


PRODUCTION = False
INSTANCE = "stage"
MAINT = False
ADMIN_NAME = "class2go example"
ADMIN_EMAIL = "crash@class.stanford.edu"
SNIPPET_EMAIL = "c2g-dev@cs.stanford.edu"
DJANGO_SECRET = "class2go"


# APPS

APPS =  ({
    "class2go": {
    "SERVER_NAME": "https://example.class.university.edu",
    "SERVER_ALIAS": "*.example.class.university.edu",
    "GIT_BRANCH": "origin/master",
    "USE_SHIB":  False,
    "SHIB_ID": "1234567890",
    "GIT_REPO": "https://github.com/Stanford-Online/class2go.git"
}}
)

#REDIRECTS
REDIRECTS = (
    { "class2go": {'FROM':  "db-class.org", 'TO': 'class2go.stanford.edu/db'} }
)
# DBCLASSCOM
FROM = "db-class.com"
TO = "class2go.stanford.edu/db"

#UTIL
CELERY_DATABASE = "/opt/class2go/celery/celerydb.sqlite"
CELERY_TIMEOUT = "7200"
CELERY_CONCURRENCY = "8"

# DNS_EDITOR
ZONE = "c2gops.com"
TTL = 300

GRADER_ENDPOINT = "http://xxxxxxxxxxxxxxxxxxxxx/yyyyyyyyyyyy"

# PIAZZA
PIAZZA_ENDPOINT = "https://piazza.com/basic_lti"
PIAZZA_KEY = "hhhhhhhhhhhh"
PIAZZA_SECRET = "ggggggggggggggg"

SCALYR_WRITE_KEY = "1234567890"

# GOOGLE
YT_SERVICE_DEVELOPER_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GOOGLE_CLIENT_ID = "nnnnnnnnnnnn.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "sssssssssssssssssssss"


USE_SHIB = False
SHIB_ID = "1234567890"

