name "util"
description "sophi utility node"

override_attributes({
    "sophi-bitnami-django" => {
            "django-app" => "util"
            }
})

run_list(
#   "recipe[chef-client]",
    "recipe[sophi-update]",
#    "recipe[gdata]",
    "recipe[sophi-base]",
    "recipe[sophi-python]",
#    "recipe[sophi-bitnami-django]",
    "recipe[sophi-deploy]",
    "recipe[sophi-logging]",
    "recipe[sophi-database.py]",
#    "recipe[sophi-collectstatic]",
    "recipe[sophi-kelvinator]",
    "recipe[s3cmd]"
#    "recipe[sophi-bitnami-apache-restart]"
)
