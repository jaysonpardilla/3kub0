#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from cloudinary import api as cloudinary_api
from django.conf import settings

print("=" * 80)
print("CHECKING CLOUDINARY RESOURCES")
print("=" * 80)

# Search for user_profiles in Cloudinary
try:
    result = cloudinary_api.resources(type='upload', prefix='ekubo/media/user_profiles', max_results=5)
    print(f"\nResources with prefix 'ekubo/media/user_profiles':")
    if result.get('resources'):
        for res in result['resources']:
            print(f"  Public ID: {res['public_id']}")
            print(f"    URL: https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{res['public_id']}")
    else:
        print("  No resources found")
except Exception as e:
    print(f"Error: {e}")

# Also search for just user_profiles
try:
    result = cloudinary_api.resources(type='upload', prefix='user_profiles', max_results=5)
    print(f"\nResources with prefix 'user_profiles':")
    if result.get('resources'):
        for res in result['resources']:
            print(f"  Public ID: {res['public_id']}")
    else:
        print("  No resources found")
except Exception as e:
    print(f"Error: {e}")

# Search for the specific file
try:
    result = cloudinary_api.resources(type='upload', prefix='ekubo/media/user_profiles/FB_IMG_1729318205270', max_results=5)
    print(f"\nResources with prefix 'ekubo/media/user_profiles/FB_IMG_1729318205270':")
    if result.get('resources'):
        for res in result['resources']:
            print(f"  Public ID: {res['public_id']}")
    else:
        print("  No resources found")
except Exception as e:
    print(f"Error: {e}")
