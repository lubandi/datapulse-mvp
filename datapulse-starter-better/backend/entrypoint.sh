#!/bin/sh
set -e

echo "==> Running migrations..."
python manage.py makemigrations authentication datasets rules checks reports scheduling --noinput
python manage.py migrate --noinput

echo "==> Seeding default users..."
python manage.py seed_users || true

echo "==> Starting Gunicorn..."
exec gunicorn datapulse.wsgi:application -c gunicorn.conf.py
