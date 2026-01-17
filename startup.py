#!/usr/bin/env python
"""
Startup script that handles migrations and starts Daphne server.
Uses os.execvp to replace the process (proper signal handling).
"""
import os
import sys

# Set up Django path and environment
os.chdir('/app/core')
sys.path.insert(0, '/app/core')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
import django
django.setup()

# Run migrations
try:
    from django.core.management import call_command
    print("Running migrations...")
    call_command('migrate', verbosity=1)
    print("Migrations completed successfully!")
except Exception as e:
    print(f"Warning: Migration error: {e}")
    print("Continuing with server startup...")

# Start Daphne (this replaces the current process)
print("Starting Daphne server...")
os.execvp('daphne', [
    'daphne',
    '-b', '0.0.0.0',
    '-p', '8000',
    'core.asgi:application'
])
