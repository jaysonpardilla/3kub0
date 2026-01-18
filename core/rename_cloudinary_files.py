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
print("RENAMING MALFORMED FILES IN CLOUDINARY")
print("=" * 80)

# List all resources with malformed names
try:
    result = cloudinary_api.resources(type='upload', max_results=100)
    malformed_files = []
    
    if result.get('resources'):
        for res in result['resources']:
            public_id = res['public_id']
            # Find ones that start with https:/res.cloudinary.com
            if public_id.startswith('https:/res.cloudinary.com/'):
                malformed_files.append(public_id)
    
    print(f"Found {len(malformed_files)} malformed files in Cloudinary\n")
    
    # Rename each file
    for old_public_id in malformed_files:
        # Extract the correct public_id from the malformed one
        if '/image/upload/' in old_public_id:
            new_public_id = old_public_id.split('/image/upload/')[-1]
            
            try:
                # Use the rename method
                result = cloudinary_api.rename(old_public_id, new_public_id)
                print(f"✓ Renamed:")
                print(f"  FROM: {old_public_id[:60]}...")
                print(f"  TO:   {new_public_id}")
            except Exception as e:
                print(f"✗ Error renaming {old_public_id[:50]}...")
                print(f"  Error: {e}")
    
    print("\n" + "=" * 80)
    if len(malformed_files) > 0:
        print("✅ FILES RENAMED IN CLOUDINARY!")
        print("   Images should now display correctly.")
    else:
        print("✅ NO MALFORMED FILES FOUND")
        
except Exception as e:
    print(f"Error: {e}")
