name "appserver"
description "Class2Go appserver node"

override_attributes({ 
    "chef-client" => {"interval" => "300"}
})

run_list(
    "recipe[chef-client]",
    "recipe[gdata]",
    "recipe[class2go-base]",
    "recipe[class2go-bitnami-django]",
    "recipe[class2go-deploy]",
    "recipe[class2go-database.py]",
    "recipe[class2go-collectstatic]"   # restarts apache
)
