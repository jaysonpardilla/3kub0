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
    Return the profile image URL or a fallback placeholder avatar.
    Usage in templates: {{ profile|profile_image_url }}
    """
    try:
        if profile_obj and profile_obj.profile and profile_obj.profile.url:
            return profile_obj.profile.url
    except:
        pass
    
    # Return a placeholder avatar URL
    if profile_obj and profile_obj.user:
        username = profile_obj.user.username or profile_obj.user.email
        return f"https://ui-avatars.com/api/?name={username}&background=random&size=128"
    
    return "https://ui-avatars.com/api/?name=User&background=random&size=128"

