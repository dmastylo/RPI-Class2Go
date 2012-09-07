#!/bin/bash -x
#
# Assumes current working directory is root of repo (class2go)
# Can't be run with "-e" flag since I'm using exit status of grep
#

if [[ -r main/database.py ]]; then
    echo "Checking to see if OK to clobber this database.py"
    grep 'INSTANCE = "jenkins"' main/database.py
    if [[ $? -eq 0 ]]; then
        echo "Looks like it's mine, clobbering"
        cp main/jenkins/database_ci.py main/database.py
    else
        echo "Hey, this isn't mine, failing"
        exit 1
    fi
else
    cp -n main/jenkins/database_ci.py main/database.py
fi

