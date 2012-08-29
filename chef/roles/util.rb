name "util"
description "Class2Go utility node"

override_attributes({
    "class2go-bitnami-django" => {
            "django-app" => "util"
            }
})

run_list(
#   "recipe[chef-client]",
    "recipe[class2go-update]",
    "recipe[gdata]",
    "recipe[class2go-base]",
    "recipe[class2go-python]",
    "recipe[class2go-bitnami-django]",
    "recipe[class2go-deploy]",
    "recipe[class2go-logging]",
    "recipe[class2go-database.py]",
#    "recipe[class2go-collectstatic]",
    "recipe[class2go-kelvinator]",
    "recipe[class2go-bitnami-apache-restart]"
)
