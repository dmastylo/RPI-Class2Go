#!/bin/bash -ex

cp database_ci.py ../database.py

cd ..
python manage.py syncdb
python manage.py migrate
python manage.py db_populate

