name "app"
description "class2go app server"

override_attributes \
    "system" => {
        "admin_user" =>  "bitnami",
        "admin_group" => "bitnami",
        "admin_home" =>  "/home/bitnami"
    }

run_list(
    "recipe[class2go-apt-update]",
    "recipe[gdata]",
    "recipe[class2go-base-ubuntu]",
    "recipe[class2go-apache]",
    "recipe[class2go-python]",
#    "recipe[bitnami-shib]",
    "recipe[class2go-deploy]",
    "recipe[class2go-logging]",
    "recipe[class2go-ops-dns]",
    "recipe[class2go-database-config]",
    "recipe[class2go-collectstatic]",
    "recipe[class2go-apache-restart]"
)
