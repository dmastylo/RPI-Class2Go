name "appserver"
description "Class2Go appserver node"

run_list(
  "recipe[hostname]",
  "recipe[class2go-base]"
  "recipe[class2go-deploy]"
  "recipe[class2go-bitnami-config]"
)
