#!/bin/bash -e 
#
# A bunch of hardcoded assumptions in here
# - your hostname doesn't have "prod" in it
# - your db is named class2go
# - you have set up your .my.cnf so you can run mysql client locally

# For reference, my ~/.my.cnf looks like this (sans comments of course):
# 
# [client]
#     host=localhost
#     user=root
#     password=root
#     database=class2go
#

HOSTNAME=`hostname`
INVALID_HOSTNAME="prod"
DEV_DB_NAME="class2go"

if [[ $HOSTNAME =~ ${INVALID_HOSTNAME} ]]; then
    echo "This script is so dangerous I won't let you run it on any machine"
    echo "that has \"${INVALID_HOSTNAME}\" in the hostname. Sorry."
    exit 1
fi

echo "This script nukes your dev database and recreates with default contents."
read -p "Are you you want to do this? (y/n) " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    exit 0
fi

DATABASES=`mysql --batch -e "show databases;"`

if [[ ! $DATABASES =~ $DEV_DB_NAME ]]; then
    echo
    echo "Error: I can't find a database named \"${DEV_DB_NAME}\"."
    echo "- maybe you've named your dev database something else?"
    echo "- maybe mysql is misconfigured (missing ~/.my.cnf)?"
    echo "Bailing out"
    exit 1
fi

if [[ $DATABASES =~ $INVALID_HOSTNAME ]]; then
    echo 
    echo "Error: I see you have a database containing the name \"${INVALID_HOSTNAME}\" in it."
    echo "Stopping since this might be an indication of a production database."
    echo "Bailing out"
    exit 1
fi
    
set -x

mysql --batch -e "drop database ${DEV_DB_NAME}; create database ${DEV_DB_NAME};"
./manage.py syncdb --noinput
./manage.py syncdb --noinput --database=celery
./manage.py migrate
./manage.py syncdb --database=celery
./manage.py db_populate

echo "Everything worked like a champ!"

