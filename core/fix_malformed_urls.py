#!/usr/bin/env python
"""
Fix script for malformed Cloudinary URLs in database.

IMPORTANT: This script does NOT fix malformed URLs by changing the database values.
Why? Because Django ImageField stores the public_id, not the full URL. If the
public_id is malformed (e.g., contains "https://res.cloudinary.com"), it means
the file was uploaded to Cloudinary with that malformed name.

The CORRECT fix is:
1. Delete the malformed files from Cloudinary
2. Re-upload the images from local files OR
3. Clear the image fields if local files don't exist

This script checks for malformed URLs and provides instructions.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chat.models import Profile
from products.models import Category, Product, Business


def check_malformed(name):
    """Check if a value is a malformed Cloudinary URL."""
    if not name:
        return False
    return 'https://res.cloudinary.com' in str(name)


def main():
    print("=" * 80)
    print("CHECKING FOR MALFORMED CLOUDINARY URLS IN DATABASE")
    print("=" * 80)

    issues_found = []

    # Check Profiles
    print("\nChecking Profiles...")
    for profile in Profile.objects.all():
        if profile.profile and check_malformed(profile.profile.name):
            issues_found.append(('Profile', profile.user.username, profile.profile.name))
            print(f"  ISSUE: {profile.profile.name[:60]}...")

    # Check Categories
    print("\nChecking Categories...")
    for cat in Category.objects.all():
        if cat.image and check_malformed(cat.image.name):
            issues_found.append(('Category', cat.name, cat.image.name))
            print(f"  ISSUE: {cat.image.name[:60]}...")

    # Check Products
    print("\nChecking Products...")
    for product in Product.objects.all():
        for field_name in ['product_image', 'product_image1', 'product_image2', 'product_image3', 'product_image4']:
            field = getattr(product, field_name, None)
            if field and field.name and check_malformed(field.name):
                issues_found.append(('Product', f"{product.product_name}.{field_name}", field.name))
                print(f"  ISSUE: {product.product_name}.{field_name}: {field.name[:60]}...")

    # Check Businesses
    print("\nChecking Businesses...")
    for business in Business.objects.all():
        if business.business_image and check_malformed(business.business_image.name):
            issues_found.append(('Business', business.business_name, f"image: {business.business_image.name}"))
            print(f"  ISSUE: {business.business_name}.image: {business.business_image.name[:60]}...")
        if business.business_logo and check_malformed(business.business_logo.name):
            issues_found.append(('Business', business.business_name, f"logo: {business.business_logo.name}"))
            print(f"  ISSUE: {business.business_name}.logo: {business.business_logo.name[:60]}...")

    print("\n" + "=" * 80)
    print(f"FOUND {len(issues_found)} MALFORMED URLS IN DATABASE")
    print("=" * 80)

    if issues_found:
        print("""
WHAT THIS MEANS:
The database contains public_ids that include full Cloudinary URLs.
This is WRONG - the public_id should be just the path, like:
    CORRECT: product_images/bg_myimage.png
    WRONG:   https://res.cloudinary.com/.../product_images/bg_myimage.png

CAUSE:
This happens when code mistakenly stores a URL instead of the file path.
The fix is to CLEAR these fields and re-upload images properly.

DO NOT MANUALLY EDIT THESE VALUES IN THE DATABASE!
Instead, go to your Django admin and re-upload the images.
""")
    else:
        print("No malformed URLs found! Your database is clean.")

    print("\n" + "=" * 80)
    print("RECOMMENDED ACTIONS")
    print("=" * 80)
    print("""
1. Delete malformed files from Cloudinary console:
   - Look for files with names containing "https://res.cloudinary.com"
   - These are orphan files with malformed public_ids

2. Re-upload images through Django admin:
   - Go to your app's admin interface
   - Edit each product/profile/category
   - Upload a new image (or clear and save to use placeholder)

3. The build_cloudinary_url() function will handle existing malformed values
   by extracting the correct public_id when building URLs for display.
""")


if __name__ == '__main__':
    main()
