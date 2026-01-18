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
    
    # Return a placeholder avatar URL with user initials
    if profile_obj and profile_obj.user:
        user = profile_obj.user
        # Get initials from first_name and last_name
        first_initial = user.first_name[0] if user.first_name else ""
        last_initial = user.last_name[0] if user.last_name else ""
        initials = f"{first_initial}{last_initial}".strip()
        
        if not initials:
            # Fall back to username or email
            initials = (user.username or user.email or "User")[:2]
        
        return f"https://ui-avatars.com/api/?name={initials}&background=random&size=128"
    
    return "https://ui-avatars.com/api/?name=User&background=random&size=128"

