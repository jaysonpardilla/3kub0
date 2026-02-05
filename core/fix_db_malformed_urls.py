#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chat.models import Profile
from products.models import Product, Category, Business

print("=" * 80)
print("FIXING DATABASE RECORDS WITH MALFORMED CLOUDINARY URLs")
print("=" * 80)

fixed_count = 0

# Fix Profile records
print("\n--- Checking Profile records ---")
for p in Profile.objects.all():
    if p.profile:
        name = p.profile.name
        if name and name.startswith('https:/res.cloudinary.com/'):
            print(f"Found malformed URL in Profile {p.user.username}: {name[:60]}...")
            # Clear the image reference (user needs to re-upload)
            p.profile = None
            p.save()
            fixed_count += 1
            print(f"  Cleared image reference")

# Fix Business records
print("\n--- Checking Business records ---")
for b in Business.objects.all():
    if b.business_image:
        name = b.business_image.name
        if name and name.startswith('https:/res.cloudinary.com/'):
            print(f"Found malformed URL in Business {b.business_name}: {name[:60]}...")
            b.business_image = None
            b.save()
            fixed_count += 1
            print(f"  Cleared business_image reference")
    
    if b.business_logo:
        name = b.business_logo.name
        if name and name.startswith('https:/res.cloudinary.com/'):
            print(f"Found malformed URL in Business {b.business_name}: {name[:60]}...")
            b.business_logo = None
            b.save()
            fixed_count += 1
            print(f"  Cleared business_logo reference")

# Fix Category records
print("\n--- Checking Category records ---")
for c in Category.objects.all():
    if c.image:
        name = c.image.name
        if name and name.startswith('https:/res.cloudinary.com/'):
            print(f"Found malformed URL in Category {c.name}: {name[:60]}...")
            c.image = None
            c.save()
            fixed_count += 1
            print(f"  Cleared image reference")

# Fix Product records
print("\n--- Checking Product records ---")
for prod in Product.objects.all():
    for field_name in ['product_image', 'product_image1', 'product_image2', 'product_image3', 'product_image4']:
        img = getattr(prod, field_name)
        if img:
            name = img.name
            if name and name.startswith('https:/res.cloudinary.com/'):
                print(f"Found malformed URL in Product {prod.product_name}.{field_name}: {name[:60]}...")
                setattr(prod, field_name, None)
                prod.save()
                fixed_count += 1
                print(f"  Cleared {field_name} reference")

print("\n" + "=" * 80)
print("FIX COMPLETE")
print("=" * 80)
print(f"\nFixed {fixed_count} database records with malformed Cloudinary URLs.")
print("\n[NOTE] These images have been cleared from the database.")
print("       Please re-upload the images through the Django admin or app.")
print("       The images will be properly stored in Cloudinary with correct public IDs.")
