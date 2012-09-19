name "report"
description "class2go reporting, feature on top of a UBUNTU util machine"

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
    "recipe[class2go-database-config]",
    "recipe[s3cmd]",
    "recipe[class2go-reports]"
)
