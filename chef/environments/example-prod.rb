name "prod"
description "Class2Go Production Environment"

default_attributes "aws" => {  
    "database_host" => "prod.AAAAAAAAAAAA.us-west-2.rds.amazonaws.com",
    "storage_bucket" => "prod-c2g",
    "access_key" => "BBBBBBBBBBBBBBBBBBBB",
    "access_secret" => "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
}

