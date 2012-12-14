#!/bin/bash -ex
#
# This is meant to run as -e so failures are real
#

# JOB_NAME is set by Jenkins
JENKINS_DB_NAME="c2g_jenkins_${JOB_NAME}"
HOSTNAME=`hostname`
INVALID_HOSTNAME="prod"
PROD_DB_NAME="class2go"

if [[ $HOSTNAME =~ ${INVALID_HOSTNAME} ]]; then
    echo "This script is so dangerous I won't let you run it on any machine"
    echo "that has \"${INVALID_HOSTNAME}\" in the hostname. Sorry."
    exit 1
fi

if [[ $JENKINS_DB_NAME =~ $INVALID_HOSTNAME ]]; then
    echo 
    echo "Error: I see the chosen database name \"${JENKINS_DB_NAME}\" contains \"${INVALID_HOSTNAME}\" in it."
    echo "Stopping since this might be an indication of a production database."
    echo "Bailing out"
    exit 1
fi

if [[ $JENKINS_DB_NAME =~ $PROD_DB_NAME ]]; then
    echo 
    echo "Error: I see the chosen database name \"${JENKINS_DB_NAME}\" contains \"${PROD_DB_NAME}\" in it."
    echo "Stopping since this might be an indication of a production database."
    echo "Bailing out"
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

# Remove the test database in case tests failed on the last run and failed
# to remove the database.
mysql --batch -e "drop database if exists test_${JENKINS_DB_NAME};"

# Make sure we have a clean database
mysql --batch -e "drop database if exists ${JENKINS_DB_NAME}; create database ${JENKINS_DB_NAME} default character set 'utf8' default collate 'utf8_unicode_ci';"

# no further database operations are needed on jenkins as the test
# runner will fire all sync and migration jobs and the tests themselves
# have database fixtures, so no need to db_populate

