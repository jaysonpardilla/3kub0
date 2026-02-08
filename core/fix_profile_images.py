#!/usr/bin/env python
"""
Script to fix Profile image URLs by extracting public_ids from malformed URLs.
"""
import sys
import os
import re

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

def fix_profile_images():
    """Fix Profile image URLs by extracting public_ids from malformed URLs."""

    from chat.models import Profile
    from django.conf import settings

    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')

    def extract_public_id_from_url(url_string):
        """Extract the actual public_id from a URL or malformed string."""
        if not url_string:
            return None

        s = str(url_string).strip()

        # Handle duplicated URL pattern: .../image/upload/v<number>/https://res.cloudinary.com/.../image/upload/<public_id>
        duplicated_pattern = r'https://res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/v\d+/https://res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/(.+)$'

        match = re.search(duplicated_pattern, s)
        if match:
            public_id = match.group(1)
            public_id = re.sub(r'^v\d+/', '', public_id)
            return public_id

        # Handle case with missing slash: https:/res.cloudinary.com/...
        duplicated_pattern_v2 = r'https://res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/v\d+/https:/res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/(.+)$'
        match = re.search(duplicated_pattern_v2, s)
        if match:
            public_id = match.group(1)
            public_id = re.sub(r'^v\d+/', '', public_id)
            return public_id

        # Handle malformed URL with missing slash: https:/res.cloudinary.com/...
        if s.startswith('https:/res.cloudinary.com/'):
            # Fix the missing slash first
            s = s.replace('https:/res.cloudinary.com/', 'https://res.cloudinary.com/')
            # Then extract the path
            path = s.replace('https://res.cloudinary.com/' + cloud_name + '/image/upload/', '')
            # Remove version prefix if present
            path = re.sub(r'^v\d+/', '', path)
            return path

        # Handle normal full Cloudinary URL - extract the public_id
        if s.startswith('https://res.cloudinary.com/'):
            # Remove the base URL and extract the path after /image/upload/
            path = s.replace('https://res.cloudinary.com/' + cloud_name + '/image/upload/', '')
            # Remove version prefix if present
            path = re.sub(r'^v\d+/', '', path)
            return path

        # If it's already a relative path (no http), return as-is
        if not s.startswith('http'):
            return s

        return None

    total_fixed = 0
    print("\n=== Fixing Profile Images ===")

    profiles = Profile.objects.all()
    for profile in profiles:
        if profile.profile and str(profile.profile):
            original_value = str(profile.profile)
            public_id = extract_public_id_from_url(original_value)

            if public_id and public_id != original_value:
                profile.profile = public_id
                profile.save()
                print(f"  Fixed profile {profile.id}: '{original_value[:50]}...' -> '{public_id}'")
                total_fixed += 1
            elif not public_id:
                print(f"  Could not extract public_id from: '{original_value[:50]}...'")

    print(f"\n=== SUMMARY ===")
    print(f"Total profiles fixed: {total_fixed}")

    if total_fixed > 0:
        print("\nProfile images have been fixed!")
    else:
        print("\nNo profile images needed fixing.")

    return total_fixed

if __name__ == '__main__':
    fix_profile_images()
