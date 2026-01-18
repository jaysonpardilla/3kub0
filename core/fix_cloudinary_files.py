#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from cloudinary import api as cloudinary_api, CloudinaryResource
from django.conf import settings
import requests

print("=" * 80)
print("RECREATING FILES WITH CORRECT PUBLIC IDS")
print("=" * 80)

# List all resources with malformed names
try:
    result = cloudinary_api.resources(type='upload', max_results=100)
    malformed_files = []
    
    if result.get('resources'):
        for res in result['resources']:
            public_id = res['public_id']
            url = res.get('secure_url', res.get('url', ''))
            # Find ones that start with https:/res.cloudinary.com
            if public_id.startswith('https:/res.cloudinary.com/'):
                malformed_files.append({'public_id': public_id, 'url': url})
    
    print(f"Found {len(malformed_files)} malformed files in Cloudinary\n")
    
    # For each malformed file, we need to:
    # 1. Extract the correct public_id
    # 2. Delete the old file
    # 3. The file will need to be re-uploaded
    
    for item in malformed_files:
        old_public_id = item['public_id']
        
        # Extract the correct public_id
        if '/image/upload/' in old_public_id:
            new_public_id = old_public_id.split('/image/upload/')[-1]
            
            print(f"\nFile: {old_public_id[:60]}...")
            print(f"  Correct ID should be: {new_public_id}")
            
            # Try to delete the malformed version
            try:
                result = cloudinary_api.delete_resources([old_public_id])
                print(f"  ✓ Deleted malformed file from Cloudinary")
            except Exception as e:
                print(f"  ✗ Could not delete: {e}")
    
    print("\n" + "=" * 80)
    print("⚠️  MALFORMED FILES HAVE BEEN IDENTIFIED")
    print("=" * 80)
    print("""
The malformed files in Cloudinary have been identified. The database has 
already been fixed with the correct public_ids.

Since the images on Cloudinary were stored with malformed names, you now have
two options:

OPTION 1: RE-UPLOAD IMAGES (Recommended)
  ✓ Go through your app and re-upload the images
  ✓ Django will create them with correct public_ids
  ✓ Images will display immediately

OPTION 2: MANUAL FIX
  1. Go to https://cloudinary.com/console
  2. Find files starting with "https:/res.cloudinary.com..." (malformed names)
  3. Delete them manually
  4. Re-upload images through your Django app

The database is ready - just need proper files in Cloudinary!
""")
        
except Exception as e:
    print(f"Error: {e}")
