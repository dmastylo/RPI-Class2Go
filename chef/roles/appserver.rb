name "appserver"
description "Class2Go appserver node"

# on't auto-run chef-client recipe until I code up proper software
# deployment tooling (see issue #196)

#override_attributes({ 
#    "chef-client" => {
#                "interval" => "300",
#                "init_style" => "none"
#        }
#})

run_list(
#   "recipe[chef-client]",
    "recipe[gdata]",
    "recipe[class2go-base]",
    "recipe[class2go-bitnami-django]",
    "recipe[class2go-deploy]",
    "recipe[class2go-database.py]",
    "recipe[class2go-collectstatic]",
    "recipe[class2go-bitnami-apache-restart]"
)
