from django import template
from products.models import Wishlist

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def in_wishlist(product, user):
    """Return True if the given product is in the user's wishlist."""
    if not user or user.is_anonymous:
        return False
    return Wishlist.objects.filter(user=user, product=product).exists()


@register.filter
def profile_image_url(profile_obj):
    """
    Returns the full Cloudinary URL for a profile image with fallback to ui-avatars.com
    Handles both relative paths (from ImageField.url) and full URLs (from model method).
    """
    try:
        if not profile_obj:
            raise ValueError("No profile object")

        # ImageField on Profile is named `profile` (profile.profile)
        img_field = getattr(profile_obj, 'profile', None)
        if img_field:
            # Try to get a usable URL or path
            url = getattr(img_field, 'url', None) or str(img_field)
            if url:
                url = url.strip()
                # If it's already a full URL (http/https), return as-is
                if url.startswith('http://') or url.startswith('https://'):
                    return url

                # Otherwise treat it as a relative path/public_id; strip MEDIA_URL if present
                from django.conf import settings
                media_url = getattr(settings, 'MEDIA_URL', '/media/') or '/media/'
                # Normalize leading slashes
                if url.startswith(media_url):
                    public_id = url[len(media_url):]
                else:
                    public_id = url.lstrip('/')

                from products.utils import build_cloudinary_url
                cloud_name = ''
                try:
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                except Exception:
                    cloud_name = 'deyrmzn1x'

                return build_cloudinary_url(public_id, cloud_name=cloud_name)
    except Exception:
        # fallthrough to placeholder
        pass

    # Fallback: Return a placeholder avatar URL with user's initials/name
    try:
        if profile_obj and getattr(profile_obj, 'user', None):
            user = profile_obj.user
            name = f"{user.first_name} {user.last_name}".strip()
            if not name:
                name = user.username or getattr(user, 'email', None) or "User"
            return f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=random&size=128"
    except Exception:
        pass

    # Ultimate fallback
    return "https://ui-avatars.com/api/?name=User&background=random&size=128"

