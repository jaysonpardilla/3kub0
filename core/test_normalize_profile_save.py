import os, django, sys
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from chat.models import Profile

p = Profile.objects.first()
print('Before:', getattr(p, 'profile', None))
malformed = 'https://res.cloudinary.com/deyrmzn1x/image/upload/v1770534410/https:/res.cloudinary.com/deyrmzn1x/image/upload/user_profiles/IMG20240810093444_khxbgv.jpg'
p.profile = malformed
p.save()
print('After:', p.profile)
