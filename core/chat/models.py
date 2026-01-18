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
                # Normalize malformed stored values containing Cloudinary host
                if 'res.cloudinary.com' in url:
                    if '/image/upload/' in url:
                        # take the last occurrence to avoid duplicated MEDIA_URL + stored full URL
                        public_id = url.split('/image/upload/')[-1]
                        from django.conf import settings
                        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                    if url.startswith('https://res.cloudinary.com/'):
                        return url
                # If it's already a full URL, return it
                if url.startswith('http://') or url.startswith('https://'):
                    return url
                # If it's a relative path (from Cloudinary storage), construct full URL
                if url:
                    from django.conf import settings
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{url}"
        except Exception:
            pass
        # Return a placeholder avatar URL (using ui-avatars service)
        return f"https://ui-avatars.com/api/?name={self.user.username}&background=random&size=128"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


