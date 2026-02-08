from arrow import now
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.BigIntegerField(null=True, blank=True)
    is_seller = models.CharField(max_length=45, choices=[('yes', 'yes'), ('no', 'no')])
    failed_attempts = models.IntegerField(default=0)
    last_failed_attempt = models.DateTimeField(null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # specify a custom related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # specify a custom related_name
        blank=True
    )


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(max_length=45, default=False)

    def __str__(self):
        return f"{self.content}"

class Profile(models.Model):
    """
    User profile model storing profile image and address information.
    
    IMPORTANT: Cloudinary URL Handling
    =================================
    When storing image paths, NEVER store a full Cloudinary URL as the public_id.
    Doing so causes 404 errors because Cloudinary treats the URL string as the filename.
    
    WRONG: https://res.cloudinary.com/deyrmzn1x/image/upload/user_profiles/avatar.png
    RIGHT: user_profiles/avatar.png
    
    The profile_image_url() method uses build_cloudinary_url() to construct
    the full URL from the stored public_id for display.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile = models.ImageField(upload_to='user_profiles', blank=True, null=True, max_length=500)  # Remove default to avoid 404 errors
    province = models.CharField(max_length=100, null=True, blank=True)
    municipality = models.CharField(max_length=100, null=True, blank=True)
    street = models.CharField(max_length=200,  null=True, blank=True)
    postal_code = models.CharField(max_length=20,  null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def is_online(self):
        """ Check if the user was active within the last 1 second """
        if self.last_seen:
            return (now() - self.last_seen).total_seconds() < 300  
            # return (now() - self.last_seen).total_seconds() < 1
        
    def __str__(self):
        return f"{self.user.username} - {self.street if self.street else 'No Address'}"
    
    def profile_image_url(self):
        """Return the full Cloudinary URL for profile image or a fallback placeholder"""
        try:
            if self.profile and getattr(self.profile, 'url', None):
                url = self.profile.url
                if url:
                    from products.utils import build_cloudinary_url
                    from django.conf import settings
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                    return build_cloudinary_url(url, cloud_name=cloud_name)
        except Exception:
            pass
        # No fallback: return empty string when no image available
        return ''

    def save(self, *args, **kwargs):
        """Ensure the profile ImageField stores only the Cloudinary public_id (relative path).

        This prevents storing full or duplicated Cloudinary URLs in the DB which
        later cause malformed display URLs.
        """
        try:
            if self.profile:
                s = str(self.profile).strip()
                # If the stored value looks like a full Cloudinary URL, extract the public_id
                if s.startswith('http') or 'res.cloudinary.com' in s:
                    import re
                    from django.conf import settings
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')

                    # Normalize missing slash variant
                    s_fixed = s.replace('https:/res.cloudinary.com/', 'https://res.cloudinary.com/')

                    if 'res.cloudinary.com' in s_fixed and '/image/upload/' in s_fixed:
                        public_part = s_fixed.split('/image/upload/')[-1]
                        # If the extracted part still contains another cloudinary URL, keep taking last segment
                        while 'res.cloudinary.com' in public_part and '/image/upload/' in public_part:
                            public_part = public_part.split('/image/upload/')[-1]

                        public_part = public_part.lstrip('/')
                        # Remove any leading version like 'v12345/'
                        public_part = re.sub(r'^v\d+/', '', public_part)
                        # Strip any leftover schema/host prefix
                        public_part = re.sub(r'https?:/*res\.cloudinary\.com[^/]*/image/upload/*', '', public_part)
                        public_part = public_part.lstrip('/')
                        if public_part:
                            # Assign the cleaned public_id back to the ImageField (Django will accept string path)
                            self.profile = public_part
        except Exception:
            pass

        return super().save(*args, **kwargs)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    # Avoid automatically saving the FileField on every User post_save —
    # this was causing unintended uploads/transformations in some setups.
    # Leave profile saving to explicit form handling or admin actions.
    return


