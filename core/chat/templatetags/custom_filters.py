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
                # Check if it's already a complete Cloudinary URL
                if url.startswith('https://res.cloudinary.com/'):
                    return url
                # Check if it's any other full URL
                if url.startswith('http://') or url.startswith('https://'):
                    return url
                
                # If it's a relative path, construct the full Cloudinary URL
                if url and not url.startswith('/'):
                    from django.conf import settings
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{url}"
                
                return url
    except:
        pass
    
    # Fallback: Return a placeholder avatar URL with user's initials/name
    if profile_obj and profile_obj.user:
        user = profile_obj.user
        # Prefer full name, fallback to username, then email
        name = f"{user.first_name} {user.last_name}".strip()
        if not name:
            name = user.username or user.email or "User"
        return f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=random&size=128"
    
    # Ultimate fallback
    return "https://ui-avatars.com/api/?name=User&background=random&size=128"
    return "https://ui-avatars.com/api/?name=User&background=random&size=128"

