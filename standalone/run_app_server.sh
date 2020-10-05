#!/bin/sh
if [ "$ENV" = "dev" ]
then
  >&2 echo "Starting Django runserver as not in prd mode"
  python /srv/standalone/manage.py runserver 0.0.0.0:80
else
  >&2 echo "Starting Gunicorn server as in prd mode"
  cd /srv/standalone && gunicorn -b 0.0.0.0:80 project.wsgi
fi
