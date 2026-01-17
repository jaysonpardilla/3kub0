#!/bin/bash
set -e

cd /app/core
python manage.py migrate
exec daphne -b 0.0.0.0 -p ${PORT:-8000} core.asgi:application
