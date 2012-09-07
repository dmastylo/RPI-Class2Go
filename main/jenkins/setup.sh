#!/bin/bash -ex
#
# Assumes current working directory is root of repo (class2go)
#

# -n prevents clobber if already there 
cp -n main/jenkins/database_ci.py main/database.py

python main/manage.py syncdb

python main/manage.py migrate

python main/manage.py db_populate

