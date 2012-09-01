name "prod"
description "Sophi Production Environment"

default_attributes \
    "aws" => {
        "database_host" => "prod.AAAAAAAAAAAA.us-west-2.rds.amazonaws.com",
        "database_instance" => "sophi",
        "database_user" => "sophi",
        "database_password" => "sophi",
        "storage_bucket" => "prod-c2g",
        "access_key" => "BBBBBBBBBBBBBBBBBBBB",
        "access_secret" => "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        "ses_user" =>  "DDDDDDDDDDDDDDDDDDDD",
        "ses_passwd" => "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
    },
    "sophi" => {
        "production" => "True",
        "admin_name" => "Sophi Operations",
        "admin_email" => "sophi-ops@cs.stanford.edu"
    },
    "piazza" => {
        "endpoint" => "https://piazza.com/basic_lti",
        "key" => "sophi",
        "secret" => "XXXXXXXXXXXXXXXXXXXXXXXXX"
    }

