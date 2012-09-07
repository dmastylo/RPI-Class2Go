#!/bin/bash -ex
#
# This is meant to run as -e so failures are real
#

python main/manage.py syncdb --noinput

python main/manage.py migrate --noinput

python main/manage.py db_populate

