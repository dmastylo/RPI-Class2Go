name "jenkins"
description "Sophi Staging Environment"

default_attributes \
    "aws" => {
        "database_host" => "jenkins.AAAAAAAAAAAA.us-west-2.rds.amazonaws.com",
        "database_instance" => "sophi",
        "database_user" => "sophi",
        "database_password" => "sophi",
        "storage_bucket" => "jenkins-c2g",
        "access_key" => "BBBBBBBBBBBBBBBBBBBB",
        "access_secret" => "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
    },
    "sophi" => {
        "production" => "False",
        "admin_name" => "Sophi Operations",
        "admin_email" => "sophi-ops@cs.stanford.edu"
    },
    "piazza" => {
        "endpoint" => "https://piazza.com/basic_lti",
        "key" => "sophi",
        "secret" => "XXXXXXXXXXXXXXXXXXXXXXXXX"
    }

