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
        if profile_obj and profile_obj.profile:
            url = profile_obj.profile.url
            
            # If URL exists, ensure it's a full Cloudinary URL
            if url:
                # If it already contains the Cloudinary host, try to normalize/extract the public_id
                if 'res.cloudinary.com' in url or url and not (url.startswith('http://') or url.startswith('https://')):
                    from products.utils import build_cloudinary_url
                    from django.conf import settings
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                    return build_cloudinary_url(url, cloud_name=cloud_name)
                # Check if it's any other full URL
                if url.startswith('http://') or url.startswith('https://'):
                    return url
                
                # If it's a relative path or public_id, construct the full Cloudinary URL
                if url:
                    from products.utils import build_cloudinary_url
                    from django.conf import settings
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                    return build_cloudinary_url(url, cloud_name=cloud_name)
    except:
        pass
    
    # Fallback: return empty string so templates receive the actual stored URL
    # (no ui-avatar replacement) — this helps debugging which URL is passed.
    try:
        return ''
    except Exception:
        return ''

