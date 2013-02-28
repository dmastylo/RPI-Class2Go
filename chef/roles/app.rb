name "app"
description "class2go app server"

override_attributes \
    "system" => {
        "admin_user" =>  "ubuntu",
        "admin_group" => "ubuntu",
        "admin_home" =>  "/home/ubuntu"
    }

run_list(
    "recipe[class2go-apt-update]",
    "recipe[gdata]",
    "recipe[class2go-base-ubuntu]",
    "recipe[class2go-python]",
    "recipe[class2go-apache]",
    "recipe[shib]",
    "recipe[class2go-deploy]",
    "recipe[class2go-logging]",
    "recipe[class2go-ops-dns]",
    "recipe[class2go-database-config]",
    "recipe[class2go-database-setup]",
    "recipe[class2go-collectstatic]",
    "recipe[class2go-apache-restart]"
)
