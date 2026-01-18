#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chat.models import Profile
from products.models import Category, Product, Business
from django.db.models import Q

print("=" * 80)
print("FIXING MALFORMED PUBLIC IDS")
print("=" * 80)

def fix_malformed_url(name):
    """
    Converts malformed public_id like:
    https:/res.cloudinary.com/deyrmzn1x/image/upload/user_profiles/FILE
    To:
    user_profiles/FILE
    """
    if not name:
        return name
    
    # If it starts with https:/res.cloudinary.com/ (MALFORMED - missing one slash)
    if name.startswith('https:/res.cloudinary.com/'):
        # Extract everything after /image/upload/
        parts = name.split('/image/upload/')
        if len(parts) > 1:
            return parts[-1]
    
    # If it starts with https://res.cloudinary.com/ (also malformed if not expected)
    if name.startswith('https://res.cloudinary.com/'):
        parts = name.split('/image/upload/')
        if len(parts) > 1:
            return parts[-1]
    
    return name

# Fix Profiles
print("\nFixing Profiles...")
profiles = Profile.objects.all()
fixed_count = 0
for profile in profiles:
    if profile.profile.name and ('https:' in str(profile.profile.name)):
        old_name = profile.profile.name
        new_name = fix_malformed_url(old_name)
        if old_name != new_name:
            profile.profile.name = new_name
            profile.save()
            fixed_count += 1
            print(f"  ✓ Fixed: {old_name[:50]}... → {new_name[:50]}...")

print(f"Profiles fixed: {fixed_count}")

# Fix Categories
print("\nFixing Categories...")
categories = Category.objects.all()
fixed_count = 0
for cat in categories:
    if cat.image.name and ('https:' in str(cat.image.name)):
        old_name = cat.image.name
        new_name = fix_malformed_url(old_name)
        if old_name != new_name:
            cat.image.name = new_name
            cat.save()
            fixed_count += 1
            print(f"  ✓ Fixed: {old_name[:50]}... → {new_name[:50]}...")

print(f"Categories fixed: {fixed_count}")

# Fix Products
print("\nFixing Products...")
products = Product.objects.all()
fixed_count = 0
for product in products:
    for field_name in ['product_image', 'product_image1', 'product_image2', 'product_image3', 'product_image4']:
        field = getattr(product, field_name, None)
        if field and field.name and ('https:' in str(field.name)):
            old_name = field.name
            new_name = fix_malformed_url(old_name)
            if old_name != new_name:
                setattr(product, field_name, new_name)
                fixed_count += 1
                print(f"  ✓ Fixed {product.product_name}: {old_name[:40]}... → {new_name[:40]}...")
    if fixed_count > 0:
        product.save()

print(f"Products fixed: {fixed_count}")

# Fix Business
print("\nFixing Businesses...")
businesses = Business.objects.all()
fixed_count = 0
for business in businesses:
    # Fix business_image
    if business.business_image.name and ('https:' in str(business.business_image.name)):
        old_name = business.business_image.name
        new_name = fix_malformed_url(old_name)
        if old_name != new_name:
            business.business_image.name = new_name
            fixed_count += 1
            print(f"  ✓ Fixed image: {old_name[:50]}... → {new_name[:50]}...")
    
    # Fix business_logo
    if business.business_logo.name and ('https:' in str(business.business_logo.name)):
        old_name = business.business_logo.name
        new_name = fix_malformed_url(old_name)
        if old_name != new_name:
            business.business_logo.name = new_name
            fixed_count += 1
            print(f"  ✓ Fixed logo: {old_name[:50]}... → {new_name[:50]}...")
    
    if fixed_count > 0:
        business.save()

print(f"Businesses fixed: {fixed_count}")

print("\n" + "=" * 80)
print("NOW YOU MUST RE-UPLOAD IMAGES TO CLOUDINARY!")
print("=" * 80)
print("""
The database has been fixed to remove malformed URLs. However, the images
themselves were uploaded to Cloudinary with malformed public_ids.

You have two options:

OPTION 1: DELETE BAD FILES AND RE-UPLOAD
  1. Go to your Cloudinary dashboard
  2. Delete all files with "https:/res.cloudinary.com..." as the name
  3. Re-upload images through your Django app

OPTION 2: RENAME FILES IN CLOUDINARY (requires API)
  This would automatically move files to correct public_ids.

For now, the database is ready. When you re-upload images, they'll have
the correct public_ids: user_profiles/FILE, product_images/FILE, etc.
""")
