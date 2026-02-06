#!/usr/bin/env python
"""
Database fix script for malformed Cloudinary URLs.

IMPORTANT: This script identifies and fixes corrupted database entries.
The fix works by:
1. Identifying image fields with malformed URLs (containing "https://res.cloudinary.com")
2. Clearing those image fields (setting to None)
3. The images in Cloudinary should be deleted separately

Why clear instead of fixing?
Because the file in Cloudinary was uploaded with a malformed public_id.
Even if we extract the correct path from the URL, the file in Cloudinary
still has the malformed name. The only way to fix it is to re-upload.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chat.models import Profile
from products.models import Category


def is_malformed(name):
    """Check if a value is a malformed Cloudinary URL."""
    if not name:
        return False
    return 'https://res.cloudinary.com' in str(name)


def main():
    print("=" * 80)
    print("FIXING CORRUPTED DATABASE ENTRIES")
    print("=" * 80)

    fixed_count = 0

    # Fix Profile Images with malformed URLs
    print("\nFixing Profile Images...")
    for profile in Profile.objects.all():
        if profile.profile and is_malformed(profile.profile.name):
            old_name = profile.profile.name
            print(f"  Found malformed: {profile.user.username}")
            print(f"    OLD: {old_name[:60]}...")
            # Clear the image field
            profile.profile = None
            profile.save()
            print(f"    NEW: (cleared - re-upload required)")
            fixed_count += 1

    # Fix Category Images with malformed URLs
    print("\nFixing Category Images...")
    for cat in Category.objects.all():
        if cat.image and is_malformed(cat.image.name):
            old_name = cat.image.name
            print(f"  Found malformed: {cat.name}")
            print(f"    OLD: {old_name[:60]}...")
            # Clear the image field
            cat.image = None
            cat.save()
            print(f"    NEW: (cleared - re-upload required)")
            fixed_count += 1

    print("\n" + "=" * 80)
    print(f"FIXED {fixed_count} DATABASE ENTRIES")
    print("=" * 80)
    print("""
NEXT STEPS:
1. Delete the malformed files from Cloudinary console:
   - Files with names containing "https://res.cloudinary.com" are orphaned
   - They can't be accessed normally and should be deleted

2. Re-upload images through Django admin:
   - Go to your app's admin
   - Edit each affected item
   - Upload a new image

3. Or run the upload_missing_media.py script to re-upload from local files
""")


if __name__ == '__main__':
    main()
