"""
Verification Script - Cloudinary Image Display Fix
This script checks if all image URLs are now properly formatted as full Cloudinary URLs.

Run this in Django shell:
python manage.py shell < verify_images.py
"""

from chat.models import Profile
from products.models import Business, Category, Product

print("=" * 80)
print("CLOUDINARY IMAGE URL VERIFICATION")
print("=" * 80)

# Check Profile Images
print("\n1. PROFILE IMAGES")
print("-" * 80)
profiles = Profile.objects.filter(profile__isnull=False, profile__gt='')[:3]
for profile in profiles:
    url = profile.profile_image_url()
    is_valid = url.startswith('https://res.cloudinary.com/') or url.startswith('https://ui-avatars.com/')
    status = "✓ VALID" if is_valid else "✗ INVALID"
    print(f"{status} | User: {profile.user.username} | URL: {url}")

if not profiles:
    print("No profile images found in database")

# Check Business Images
print("\n2. BUSINESS IMAGES")
print("-" * 80)
businesses = Business.objects.filter(business_image__isnull=False, business_image__gt='')[:2]
for business in businesses:
    url = business.business_image_url
    is_valid = url.startswith('https://res.cloudinary.com/') or url == ''
    status = "✓ VALID" if is_valid else "✗ INVALID"
    print(f"{status} | Business: {business.business_name} | URL: {url[:60]}...")

# Check Business Logos
print("\n3. BUSINESS LOGOS")
print("-" * 80)
logos = Business.objects.filter(business_logo__isnull=False, business_logo__gt='')[:2]
for business in logos:
    url = business.business_logo_url
    is_valid = url.startswith('https://res.cloudinary.com/') or url == ''
    status = "✓ VALID" if is_valid else "✗ INVALID"
    print(f"{status} | Business: {business.business_name} | URL: {url[:60]}...")

# Check Category Images
print("\n4. CATEGORY IMAGES")
print("-" * 80)
categories = Category.objects.filter(image__isnull=False, image__gt='')[:2]
for category in categories:
    url = category.category_image_url()
    is_valid = url.startswith('https://res.cloudinary.com/') or url == ''
    status = "✓ VALID" if is_valid else "✗ INVALID"
    print(f"{status} | Category: {category.name} | URL: {url[:60]}...")

# Check Product Images
print("\n5. PRODUCT IMAGES")
print("-" * 80)
products = Product.objects.filter(product_image__isnull=False, product_image__gt='')[:3]
for product in products:
    url = product.product_image_url()
    is_valid = url.startswith('https://res.cloudinary.com/') or url == ''
    status = "✓ VALID" if is_valid else "✗ INVALID"
    print(f"{status} | Product: {product.product_name[:40]} | URL: {url[:60]}...")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print("\nExpected Results:")
print("  ✓ All Cloudinary URLs should start with: https://res.cloudinary.com/deyrmzn1x/")
print("  ✓ All placeholder URLs should start with: https://ui-avatars.com/")
print("  ✓ Empty URLs should display as empty strings")
print("\nIf you see ✗ INVALID, there's still an issue to fix.")
print("\nNOTE: These URLs should now load properly in browsers!")
