#!/bin/bash -e

envs="prod stage dev"

echo "This script prepares for an install by making sure that three shared resources are"
echo "uploaded from this repo and the central Chef Server."
echo 
echo "1. updates environments from shared files: ${envs}"
echo "2. uploads roles"
echo "3. uploads cookbooks"
echo 
echo "Your current (local) git status is:"
echo "-------------------------------------------------------------"
git status
echo "-------------------------------------------------------------"

echo
read -p "Do you want to proceed? (y/n) " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    exit 0
fi


for e in $envs; do
    if [ -e environments/$e.rb ]; then
        set -x
        knife environment from file environments/$e.rb
        set +x
    fi
done

set -x

knife role from file roles/*.rb

knife cookbook upload -a
