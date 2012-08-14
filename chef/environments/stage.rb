name "stage"
description "Class2Go Staging Environment"

default_attributes "aws" => {  
    "database_host" => "stage.czjqjb57rejd.us-west-2.rds.amazonaws.com",
    "storage_bucket" => "stage-c2g",
    "access_key" => "AKIAJSOEWTA43VHEMSBA",
    "access_secret" => "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"
}

