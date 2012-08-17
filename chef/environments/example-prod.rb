name "prod"
description "Class2Go Production Environment"

default_attributes \
    "aws" => {
        "database_host" => "prod.AAAAAAAAAAAA.us-west-2.rds.amazonaws.com",
        "storage_bucket" => "prod-c2g",
        "access_key" => "BBBBBBBBBBBBBBBBBBBB",
        "access_secret" => "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
    },
    "class2go" => {
        "production" => "True",
        "admin_name" => "Class2Go",
        "admin_email" => "c2gops@gmail.com"
    }

