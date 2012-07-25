name "stage"
description "Class2Go Staging Environment"

default_attributes "bitnami_django" => { "database_host" => "appdb-stage.czjqjb57rejd.us-west-2.rds.amazonaws.com" }

