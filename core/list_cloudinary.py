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
print("CHECKING ALL CLOUDINARY RESOURCES")
print("=" * 80)

# List all resources
try:
    result = cloudinary_api.resources(type='upload', max_results=100)
    print(f"\nTotal resources in Cloudinary: {result.get('total_count', 'unknown')}")
    print(f"\nFirst 20 resources:")
    if result.get('resources'):
        for res in result['resources'][:20]:
            print(f"  - {res['public_id']}")
    else:
        print("  No resources found")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
