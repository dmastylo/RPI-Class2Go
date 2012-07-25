name "prod"
description "Class2Go Staging Environment"

default_attributes "bitnami_django" => { "database_host" => "appdb-prod.czjqjb57rejd.us-west-2.rds.amazonaws.com" }

