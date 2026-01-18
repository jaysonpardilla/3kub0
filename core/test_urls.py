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
print("CHECKING ACTUAL DATABASE URLS")
print("=" * 80)

# Check a profile image
profile = Profile.objects.filter(profile__isnull=False, profile__gt='').first()
if profile:
    print(f"\nProfile Test:")
    print(f"  Raw DB field: {profile.profile}")
    print(f"  .url property: {profile.profile.url}")
    print(f"  profile_image_url() method: {profile.profile_image_url()}")
else:
    print("\nNo profile images found")

# Check a product image
product = Product.objects.filter(product_image__isnull=False, product_image__gt='').first()
if product:
    print(f"\nProduct Test:")
    print(f"  Raw DB field: {product.product_image}")
    print(f"  .url property: {product.product_image.url}")
    print(f"  product_image_url() method: {product.product_image_url()}")
else:
    print("\nNo product images found")

# Check a category image
category = Category.objects.filter(image__isnull=False, image__gt='').first()
if category:
    print(f"\nCategory Test:")
    print(f"  Raw DB field: {category.image}")
    print(f"  .url property: {category.image.url}")
    print(f"  category_image_url() method: {category.category_image_url()}")
else:
    print("\nNo category images found")

print("\n" + "=" * 80)
