#!/bin/sh
set -eu

mkdir -p /app/logs /app/static /app/media

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
