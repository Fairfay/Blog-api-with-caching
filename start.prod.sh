#!/bin/sh
set -e

python manage.py check

python manage.py collectstatic --noinput

python manage.py migrate

gunicorn -c gunicorn.conf.py