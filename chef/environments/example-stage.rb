name "stage"
description "Class2Go Staging Environment"

default_attributes "aws" => {  
    "database_host" => "stage.AAAAAAAAAAAA.us-west-2.rds.amazonaws.com",
    "storage_bucket" => "stage-c2g",
    "access_key" => "BBBBBBBBBBBBBBBBBBBB",
    "access_secret" => "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
}

