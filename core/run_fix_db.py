import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from fix_db import fix_cloudinary_urls

if __name__ == '__main__':
    fix_cloudinary_urls()
