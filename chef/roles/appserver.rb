name "appserver"
description "class2go appserver node -- on top of BITNAMI"

override_attributes \
    "class2go-bitnami-django" => {
        "django-app" => "main"
        },
    "system" => {
        "admin_user" =>  "bitnami",
        "admin_group" => "bitnami",
        "admin_home" =>  "/home/bitnami"
    }

# For now not doing an update/upgrade before everything else since it
# can cause mysterious problems and takes so darn long.  have to do it 
# on the util machines though

run_list(
#   "recipe[chef-client]",
    "recipe[class2go-apt-update]",
    "recipe[gdata]",
    "recipe[class2go-base-bitnami]",
    "recipe[class2go-python]",
    "recipe[class2go-bitnami-django]",
    "recipe[bitnami-shib]",
    "recipe[class2go-deploy]",
    "recipe[class2go-logging]",
    "recipe[class2go-database-config]",
    "recipe[class2go-collectstatic]",
    "recipe[class2go-bitnami-apache-restart]"
)
