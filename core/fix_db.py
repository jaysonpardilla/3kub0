#!/usr/bin/env python
"""
Fix script for Cloudinary URL duplication issue.

This script:
1. Finds all products, profiles, categories, and businesses with corrupted Cloudinary URLs
2. Extracts the correct public_id from duplicated URLs
3. Updates the database with the correct values

Run with: python manage.py shell < core/fix_db.py
"""

import sys
import re

def fix_cloudinary_urls():
    """Fix all corrupted Cloudinary URLs in the database."""
    
    from products.models import Product, Business, Category
    from chat.models import Profile
    from django.conf import settings
    
    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
    
    def extract_public_id_from_duplicated(url_string):
        """
        Extract the actual public_id from a duplicated URL pattern.
        
        Example input: https://res.cloudinary.com/deyrmzn1x/image/upload/v123/https:/res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_test.png
        Example output: product_images/bg_test.png
        """
        if not url_string:
            return None
            
        s = str(url_string).strip()
        
        # Pattern to match duplicated URL: .../image/upload/v<number>/https://res.cloudinary.com/.../image/upload/<public_id>
        duplicated_pattern = r'https://res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/v\d+/https://res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/(.+)$'
        
        match = re.search(duplicated_pattern, s)
        if match:
            public_id = match.group(1)
            # Clean up any version numbers that might still be present
            public_id = re.sub(r'^v\d+/', '', public_id)
            return public_id
        
        # Also handle case with missing slash: https:/res.cloudinary.com/...
        duplicated_pattern_v2 = r'https://res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/v\d+/https:/res\.cloudinary\.com/' + re.escape(cloud_name) + r'/image/upload/(.+)$'
        match = re.search(duplicated_pattern_v2, s)
        if match:
            public_id = match.group(1)
            public_id = re.sub(r'^v\d+/', '', public_id)
            # Remove .png if it exists at the end (to avoid double extension)
            if public_id.endswith('.png'):
                public_id = public_id[:-4]
            return public_id
            
        return None
    
    def clean_image_field(field_value):
        """Clean a single image field value."""
        if not field_value:
            return field_value
            
        s = str(field_value).strip()
        
        # Check if it's a duplicated URL pattern
        public_id = extract_public_id_from_duplicated(s)
        if public_id:
            print(f"  Found duplicated URL: {s[:80]}...")
            print(f"  Extracted public_id: {public_id}")
            return public_id
        
        # Check if it's already a clean full URL (shouldn't be stored, but handle it)
        if s.startswith('https://res.cloudinary.com/') or s.startswith('https:/res.cloudinary.com/'):
            # Extract the public_id from the URL
            pattern = r'/' + re.escape(cloud_name) + r'/image/upload/(.+)$'
            match = re.search(pattern, s)
            if match:
                public_id = match.group(1)
                public_id = re.sub(r'^v\d+/', '', public_id)
                print(f"  Found full URL: {s[:80]}...")
                print(f"  Extracted public_id: {public_id}")
                return public_id
        
        # Already a relative path, return as-is
        return s
    
    total_fixed = 0
    
    # Fix Products
    print("\n=== Fixing Products ===")
    products = Product.objects.all()
    for product in products:
        fixed_fields = []
        for field_name in ['product_image', 'product_image1', 'product_image2', 'product_image3', 'product_image4']:
            field_value = getattr(product, field_name)
            if field_value and str(field_value):
                new_value = clean_image_field(str(field_value))
                if new_value != str(field_value):
                    # Update the field
                    setattr(product, field_name, new_value)
                    fixed_fields.append(field_name)
        
        if fixed_fields:
            product.save()
            print(f"  Fixed product {product.id}: {', '.join(fixed_fields)}")
            total_fixed += 1
    
    print(f"\nFixed {total_fixed} products")
    
    # Fix Profiles
    print("\n=== Fixing Profiles ===")
    profiles = Profile.objects.all()
    fixed_profiles = 0
    for profile in profiles:
        if profile.profile:
            new_value = clean_image_field(str(profile.profile))
            if new_value != str(profile.profile):
                profile.profile = new_value
                profile.save()
                print(f"  Fixed profile {profile.id}")
                fixed_profiles += 1
    
    print(f"\nFixed {fixed_profiles} profiles")
    total_fixed += fixed_profiles
    
    # Fix Categories
    print("\n=== Fixing Categories ===")
    categories = Category.objects.all()
    fixed_categories = 0
    for category in categories:
        if category.image:
            new_value = clean_image_field(str(category.image))
            if new_value != str(category.image):
                category.image = new_value
                category.save()
                print(f"  Fixed category {category.id}")
                fixed_categories += 1
    
    print(f"\nFixed {fixed_categories} categories")
    total_fixed += fixed_categories
    
    # Fix Businesses
    print("\n=== Fixing Businesses ===")
    businesses = Business.objects.all()
    fixed_businesses = 0
    for business in businesses:
        fixed_fields = []
        for field_name in ['business_image', 'business_logo']:
            field_value = getattr(business, field_name)
            if field_value and str(field_value):
                new_value = clean_image_field(str(field_value))
                if new_value != str(field_value):
                    setattr(business, field_name, new_value)
                    fixed_fields.append(field_name)
        
        if fixed_fields:
            business.save()
            print(f"  Fixed business {business.id}: {', '.join(fixed_fields)}")
            fixed_businesses += 1
    
    print(f"\nFixed {fixed_businesses} businesses")
    total_fixed += fixed_businesses
    
    print(f"\n=== SUMMARY ===")
    print(f"Total records fixed: {total_fixed}")
    print("\nDone! Please verify that images now display correctly.")
    print("If any images are still broken, re-upload them through the admin interface.")

if __name__ == '__main__':
    # When run directly with manage.py shell, execute the fix
    fix_cloudinary_urls()
