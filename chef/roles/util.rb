name "util"
description "class2go utility node"

override_attributes \
    "system" => {
        "admin_user" => "ubuntu",
        "admin_group" => "ubuntu",
        "admin_home" => "/home/ubuntu"
    }

run_list(
#   "recipe[chef-client]",
    "recipe[class2go-apt-update]",
    "recipe[gdata]",
    "recipe[class2go-base-ubuntu]",
    "recipe[class2go-python]",
    "recipe[class2go-deploy]",
    "recipe[class2go-logging]",
    "recipe[class2go-ops-dns]",
    "recipe[class2go-database-config]",
    "recipe[s3cmd]",
    "recipe[class2go-util-kelvinator]",
    "recipe[class2go-certificate]",
    "recipe[class2go-celery-worker]"
)

