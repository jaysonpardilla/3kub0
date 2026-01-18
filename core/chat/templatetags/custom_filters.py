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
    try:
        if profile_obj and profile_obj.profile and profile_obj.profile.url:
            return profile_obj.profile.url
    except:
        pass
    
    # Return a placeholder avatar URL with user's initials/name
    if profile_obj and profile_obj.user:
        user = profile_obj.user
        # Prefer full name, fallback to username, then email
        name = f"{user.first_name} {user.last_name}".strip()
        if not name:
            name = user.username or user.email or "User"
        return f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=random&size=128"
    
    return "https://ui-avatars.com/api/?name=User&background=random&size=128"

