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
print("CLEANING UP CORRUPTED URLS IN DATABASE")
print("=" * 80)

# Fix Category Images with double Cloudinary URLs
corrupted_categories = Category.objects.filter(
    image__icontains='https://res.cloudinary.com'
)

if corrupted_categories.exists():
    print(f"\nFound {corrupted_categories.count()} categories with corrupted URLs")
    for cat in corrupted_categories:
        old_value = cat.image.name
        # Extract just the public_id part (everything after the last https://res.cloudinary.com/deyrmzn1x/image/upload/)
        if 'https:/res.cloudinary.com' in cat.image.name:  # Missing one slash
            # Find the last occurrence of the cloudinary domain
            parts = cat.image.name.split('https://res.cloudinary.com/deyrmzn1x/image/upload/')
            if len(parts) > 1:
                # Get the last part which should be the actual public_id
                correct_path = parts[-1]
                cat.image.name = correct_path
                cat.save()
                print(f"  ✓ Fixed: {old_value[:50]}... → {correct_path[:50]}...")
        elif cat.image.name.startswith('https://res.cloudinary.com/'):
            # Remove the full https://res.cloudinary.com/deyrmzn1x/image/upload/ prefix
            correct_path = cat.image.name.replace('https://res.cloudinary.com/deyrmzn1x/image/upload/', '')
            cat.image.name = correct_path
            cat.save()
            print(f"  ✓ Fixed: {old_value[:50]}... → {correct_path[:50]}...")

# Fix Profile Images - remove default.png if exists
profile_with_default = Profile.objects.filter(profile='default.png')
if profile_with_default.exists():
    print(f"\nFound {profile_with_default.count()} profiles with default.png")
    for profile in profile_with_default:
        profile.profile.name = ''
        profile.save()
        print(f"  ✓ Cleared default.png for {profile.user.username}")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
