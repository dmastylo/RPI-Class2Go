name "appserver"
description "sophi appserver node"

override_attributes({
    "sophi-bitnami-django" => {
            "django-app" => "main"
            }
})


# For now not doing an update/upgrade before everything else since it
# can cause mysterious problems and takes so darn long.  have to do it 
# on the util machines though

run_list(
#   "recipe[chef-client]",
#   "recipe[sophi-update]",
    "recipe[gdata]",
    "recipe[sophi-base]",
    "recipe[sophi-python]",
    "recipe[sophi-bitnami-django]",
    "recipe[sophi-deploy]",
    "recipe[sophi-logging]",
    "recipe[sophi-database.py]",
    "recipe[sophi-collectstatic]",
    "recipe[sophi-bitnami-apache-restart]"
)
