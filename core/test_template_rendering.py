#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.template import Template, Context
from chat.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TESTING TEMPLATE RENDERING")
print("=" * 80)

# Get a user with a profile
user = User.objects.filter(profile__isnull=False).first()

if user and user.profile:
    print(f"\nUser: {user.username}")
    print(f"Profile Image DB: {user.profile.profile}")
    print(f"Profile .url: {user.profile.profile.url}")
    print(f"profile_image_url(): {user.profile.profile_image_url()}")
    
    # Now test the template filter
    from chat.templatetags.custom_filters import profile_image_url
    filter_result = profile_image_url(user.profile)
    print(f"Template filter result: {filter_result}")
    
    # Test what Django template would render
    template = Template("{{ profile|profile_image_url }}")
    from django.template import Context
    context = Context({'profile': user.profile})
    rendered = template.render(context)
    print(f"Template rendered HTML src: {rendered}")
    
    print("\n" + "=" * 80)
    print("EXPECTED IN BROWSER")
    print("=" * 80)
    print(f"""
<img src="{filter_result}" 
     alt="Profile Picture"
     data-user-name="{user.first_name} {user.last_name}"
     style="border-radius: 50%; object-fit: cover;">
    """)
else:
    print("No user with profile found")
