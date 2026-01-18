#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chat.models import Profile
from products.models import Category

print("=" * 80)
print("FIXING CORRUPTED DATABASE ENTRIES")
print("=" * 80)

# Fix Profile Images with malformed URLs
profiles_to_fix = Profile.objects.all()
for profile in profiles_to_fix:
    if profile.profile.name and ('https:/' in str(profile.profile.name) or 'http' in str(profile.profile.name)):
        # This profile has a full URL stored - extract just the public_id
        old_name = profile.profile.name
        
        # Extract the public_id part
        if 'https:/res.cloudinary.com' in old_name:  # Missing one slash malformed URL
            # Extract everything after the LAST occurrence of /image/upload/
            if '/image/upload/' in old_name:
                parts = old_name.rsplit('/image/upload/', 1)
                if len(parts) == 2:
                    correct_path = parts[1]
                    profile.profile.name = correct_path
                    profile.save()
                    print(f"✓ Profile {profile.user.username}: Fixed URL storage")
                    print(f"  From: {old_name[:60]}...")
                    print(f"  To:   {correct_path[:60]}...")

# Fix Category Images with malformed URLs  
categories_to_fix = Category.objects.all()
for cat in categories_to_fix:
    if cat.image.name and ('https:/' in str(cat.image.name) or 'http' in str(cat.image.name)):
        # This category has a full URL stored - extract just the public_id
        old_name = cat.image.name
        
        # Extract the public_id part
        if 'https:/res.cloudinary.com' in old_name or '/image/upload/' in old_name:
            # Extract everything after the LAST occurrence of /image/upload/
            if '/image/upload/' in old_name:
                parts = old_name.rsplit('/image/upload/', 1)
                if len(parts) == 2:
                    correct_path = parts[1]
                    cat.image.name = correct_path
                    cat.save()
                    print(f"✓ Category {cat.name}: Fixed URL storage")
                    print(f"  From: {old_name[:60]}...")
                    print(f"  To:   {correct_path[:60]}...")

print("\n" + "=" * 80)
print("DATABASE CLEANUP COMPLETE")
print("=" * 80)
