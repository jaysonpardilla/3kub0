#!/usr/bin/env python
"""Minimal startup to test if container can run Python at all"""
import sys
import subprocess
import os

print("=== DEBUG: Python Startup Script Started ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")

# Try to change directory
try:
    os.chdir('/app/core')
    print(f"Changed to: {os.getcwd()}")
except Exception as e:
    print(f"ERROR changing directory: {e}")
    sys.exit(1)

# Check if manage.py exists
if os.path.exists('manage.py'):
    print("✓ manage.py found")
else:
    print("✗ manage.py NOT found - listing /app/core:")
    os.system('ls -la /app/core')
    sys.exit(1)

# Check if we can import Django
try:
    import django
    print(f"✓ Django {django.get_version()} imported")
except Exception as e:
    print(f"✗ Django import failed: {e}")
    sys.exit(1)

# Try to run migrations
print("\n=== Running Migrations ===")
try:
    result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    if result.returncode != 0:
        print(f"Migration failed with return code {result.returncode}")
except Exception as e:
    print(f"Migration error: {e}")

# Collect static files
print("\n=== Collecting Static Files ===")
try:
    result = subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    if result.returncode != 0:
        print(f"Collectstatic failed with return code {result.returncode}")
except Exception as e:
    print(f"Collectstatic error: {e}")

# Try to start Daphne
print("\n=== Starting Daphne ===")
try:
    subprocess.call([
        sys.executable, '-m', 'daphne',
        '-b', '0.0.0.0',
        '-p', '8000',
        'core.asgi:application'
    ])
except Exception as e:
    print(f"ERROR starting Daphne: {e}")
    sys.exit(1)
