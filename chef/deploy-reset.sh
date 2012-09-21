#!/bin/bash -e

echo "This script prepares for an install by making sure that three shared resources are"
echo "uploaded from this repo and the central Chef Server."
echo 
echo "1. updates the stage and prod environments from shared files"
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

set -x

knife environment from file environments/prod.rb
knife environment from file environments/stage.rb

knife role from file roles/*.rb

knife cookbook upload -a
