name "stage"
description "Sophi Staging Environment"

default_attributes \
        # AWS GLOBAL
        "access_key" => "aaaaaaaaaaaaaaaaaaaa",
        "access_secret" => "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        # RDS
        "database_host" => "stage.cccccccccccc.us-west-2.rds.amazonaws.com",
        "database_instance" => "sophi",
        "database_user" => "sophi",
        "database_password" => "dddddddddd",    # minimum 8 chars
        # S3
        "storage_bucket" => "stage-c2g",
        # SES
        "smtp_user" => "eeeeeeeeeeeeeeeeeeee",
        "smtp_password" => "ffffffffffffffffffffffffffffffffffffffffffff"
    },
    "main" => {
        "production" => "False",
        "admin_name" => "Sophi Development",
        "admin_email" => "sophi-dev@cs.stanford.edu",
        "django_secret" => "sophi"
    },
    "util" => {
        "celery_database" => "/opt/sophi/celery/celerydb.sqlite"
    },
    "piazza" => {
        "endpoint" => "https://piazza.com/basic_lti",
        "key" => "class2go",        # old test account, OK
        "secret" => "ggggggggggggggg"
    }
