#!/bin/bash -ex
#
# This is meant to run as -e so failures are real
#

JENKINS_DB_NAME=${C2G_JENKINS_DBNAME:-"c2g-jenkins"}
HOSTNAME=`hostname`
INVALID_HOSTNAME="prod"

if [[ $HOSTNAME =~ ${INVALID_HOSTNAME} ]]; then
    echo "This script is so dangerous I won't let you run it on any machine"
    echo "that has \"${INVALID_HOSTNAME}\" in the hostname. Sorry."
    exit 1
fi

DATABASES=`mysql --batch -e "show databases;"`
if [[ $DATABASES =~ $INVALID_HOSTNAME ]]; then
    echo 
    echo "Error: I see you have a database containing the name \"${INVALID_HOSTNAME}\" in it."
    echo "Stopping since this might be an indication of a production database."
    echo "Bailing out"
    exit 1
fi

mysql --batch -e "drop database if exists ${JENKINS_DB_NAME}; create database ${JENKINS_DB_NAME} default character set 'utf8' default collate 'utf8_unicode_ci';"

python main/manage.py syncdb --noinput

python main/manage.py migrate --noinput

python main/manage.py db_populate

