name "appserver"
description "Sophi appserver node -- on top of BITNAMI"

override_attributes \
    "sophi-bitnami-django" => {
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
    "recipe[sophi-apt-update]",
    "recipe[gdata]",
    "recipe[sophi-base-bitnami]",
    "recipe[sophi-python]",
    "recipe[sophi-bitnami-django]",
    "recipe[sophi-deploy]",
    "recipe[sophi-logging]",
    "recipe[sophi-database-config]",
    "recipe[sophi-collectstatic]",
    "recipe[sophi-bitnami-apache-restart]"
)
