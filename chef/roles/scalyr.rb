name "scalyr"
description "add scalyr reporting to a server"

run_list(
    "recipe[scalyr-agent]"
)
