#!/bin/sh
# Runs migrations on start for the API container only (the worker skips them).
set -e
if [ "$RUN_MIGRATIONS" = "1" ]; then
  python manage.py migrate --noinput
fi
exec "$@"
