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
        # Normalize variants like 'https:/res.cloudinary.com' -> 'https://res.cloudinary.com'
        s = s.replace('https:/res.cloudinary.com/', 'https://res.cloudinary.com/')

        # If the string contains a Cloudinary URL (possibly duplicated/nested),
        # take the substring after the last '/image/upload/' and strip any
        # version prefix or leftover schema/host fragments.
        if 'res.cloudinary.com' in s and '/image/upload/' in s:
            public_id = s.split('/image/upload/')[-1]
            # If the extracted part still contains another cloudinary URL, keep taking last segment
            while 'res.cloudinary.com' in public_id and '/image/upload/' in public_id:
                public_id = public_id.split('/image/upload/')[-1]

            public_id = public_id.lstrip('/')
            # Remove any leading version like 'v12345/'
            public_id = re.sub(r'^v\d+/', '', public_id)
            # Strip any leftover schema/host prefix (e.g. 'https:/res.cloudinary.com/.../image/upload/')
            public_id = re.sub(r'https?:/*res\.cloudinary\.com[^/]*/image/upload/*', '', public_id)
            public_id = public_id.lstrip('/')
            return public_id if public_id else None

        # If it's a full (but not nested) Cloudinary URL, extract path after /image/upload/
        if s.startswith('https://res.cloudinary.com/'):
            path = s.replace('https://res.cloudinary.com/' + cloud_name + '/image/upload/', '')
            path = re.sub(r'^v\d+/', '', path)
            return path.lstrip('/') if path else None

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
