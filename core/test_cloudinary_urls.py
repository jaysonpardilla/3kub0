#!/usr/bin/env python
import os
import sys
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chat.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TESTING CLOUDINARY URLS DIRECTLY")
print("=" * 80)

# Get profiles with images
profiles = Profile.objects.filter(profile__isnull=False, profile__gt='')[:3]

for profile in profiles:
    url = profile.profile_image_url()
    print(f"\nUser: {profile.user.username}")
    print(f"  URL: {url}")
    
    # Try to fetch the URL
    try:
        response = requests.head(url, timeout=5)
        print(f"  Status Code: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print(f"  ✅ URL IS VALID")
        else:
            print(f"  ❌ URL RETURNED: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ ERROR FETCHING URL: {str(e)}")

print("\n" + "=" * 80)
print("CHECKING SETTINGS")
print("=" * 80)

from django.conf import settings

print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"SECURE_SSL_REDIRECT: {settings.SECURE_SSL_REDIRECT}")
print(f"CLOUDINARY_STORAGE: {settings.CLOUDINARY_STORAGE}")
