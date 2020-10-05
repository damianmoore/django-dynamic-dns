#!/bin/sh

PYTHONPATH=.

>&2 echo "Migrating database"
python manage.py migrate

>&2 echo "Ensuring admin user exists"
python manage.py create_admin_user

>&2 echo "Starting supervisor"
supervisord -c supervisord.conf
