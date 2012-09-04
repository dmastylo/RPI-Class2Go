name "util"
description "Sophi utility node -- on top of UBUNTU"

override_attributes \
    "system" => {
        "admin_user" => "ubuntu",
        "admin_group" => "ubuntu",
        "admin_home" => "/home/ubuntu"
    }

run_list(
#   "recipe[chef-client]",
    "recipe[sophi-apt-update]",
    "recipe[gdata]",
    "recipe[sophi-base-ubuntu]",
    "recipe[sophi-python]",
    "recipe[sophi-deploy]",
    "recipe[sophi-logging]",
    "recipe[sophi-database-config]",
    "recipe[s3cmd]",
    "recipe[sophi-util-kelvinator]",
    "recipe[sophi-celery-worker]"
)
