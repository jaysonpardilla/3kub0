#!/bin/bash
cd core
python manage.py migrate
daphne -b 0.0.0.0 -p ${PORT:-8000} core.asgi:application
