#!/bin/bash -ex
#
# This is meant to run as -e so failures are real
#

dbname=${C2G_JENKINS_DBNAME:-"class2go"}

mysql --batch -e "drop database ${dbname} if exists; create database ${dbname} default character set 'utf8' default collate 'utf8_unicode_ci';"

python main/manage.py syncdb --noinput

python main/manage.py migrate --noinput

python main/manage.py db_populate

