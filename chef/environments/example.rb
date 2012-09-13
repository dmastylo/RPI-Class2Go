# The General Rule: only make additions to this file, or change values.
# Changing the keys themselves would have to be done in conjunction with
# all recipes using it, which is tricky since Chef is a shared resource.
 
name "example"
description "class2go Example Environment"

default_attributes \
    "aws" => {
        # AWS GLOBAL
        "access_key" => "aaaaaaaaaaaaaaaaaaaa",
        "access_secret" => "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        # RDS
        "database_host" => "env.cccccccccccc.us-west-2.rds.amazonaws.com",
        "database_instance" => "class2go",
        "database_user" => "xxxxxxxxxxxx",
        "database_password" => "dddddddddd",
        # S3
        "storage_bucket" => "stage-c2g",
        # SES
        "smtp_user" => "eeeeeeeeeeeeeeeeeeee",
        "smtp_password" => "ffffffffffffffffffffffffffffffffffffffffffff"
    },
    "main" => {
        "production" => "False",
        "instance" => "stage",
        "admin_name" => "Class2Go Example",
        "admin_email" => "c2g-dev@cs.stanford.edu",
        "django_secret" => "class2go"
    },
    "util" => {
        "celery_database" => "/opt/class2go/celery/celerydb.sqlite"
    },
    "piazza" => {
        "endpoint" => "https://piazza.com/basic_lti",
        "key" => "hhhhhhhhhhhh",
        "secret" => "ggggggggggggggg"
    },
    "google" => {
        "yt_service_developer_key" => "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "google_client_id" => "nnnnnnnnnnnn.apps.googleusercontent.com",
        "google_client_secret" => "sssssssssssssssssssss"
    }
