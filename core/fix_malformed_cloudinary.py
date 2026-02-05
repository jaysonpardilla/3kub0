#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from cloudinary import api as cloudinary_api, uploader
from django.conf import settings
from pathlib import Path

BASE_DIR = Path(settings.BASE_DIR)
MEDIA_ROOT = BASE_DIR / 'media'

print("=" * 80)
print("FIXING MALFORMED CLOUDINARY FILES")
print("=" * 80)

# List all resources
try:
    result = cloudinary_api.resources(type='upload', max_results=100)
    malformed_files = []
    correct_files = []
    
    if result.get('resources'):
        for res in result['resources']:
            public_id = res['public_id']
            secure_url = res.get('secure_url', '')
            # Find ones that start with https:/res.cloudinary.com (malformed)
            if public_id.startswith('https:/res.cloudinary.com/'):
                malformed_files.append({'public_id': public_id, 'url': secure_url})
            else:
                correct_files.append(public_id)
    
    print(f"Found {len(malformed_files)} MALFORMED files in Cloudinary")
    print(f"Found {len(correct_files)} correctly named files\n")
    
    if not malformed_files:
        print("No malformed files found!")
    
    # Delete all malformed files
    print("\n" + "-" * 40)
    print("DELETING MALFORMED FILES")
    print("-" * 40)
    
    old_public_ids = [f['public_id'] for f in malformed_files]
    
    if old_public_ids:
        try:
            result = cloudinary_api.delete_resources(old_public_ids)
            print(f"Deleted {len(old_public_ids)} malformed files from Cloudinary")
        except Exception as e:
            print(f"Error deleting files: {e}")
    
    # Now try to re-upload from local files
    print("\n" + "-" * 40)
    print("RE-UPLOADING FROM LOCAL MEDIA FILES")
    print("-" * 40)
    
    from chat.models import Profile
    from products.models import Product, Category, Business
    
    targets = []
    
    # Check Profile images
    for p in Profile.objects.all():
        if p.profile and p.profile.name:
            targets.append(('Profile', p.user.username if p.user else str(p.id), p.profile.name))
    
    # Check Business images
    for b in Business.objects.all():
        if b.business_image and b.business_image.name:
            targets.append(('Business.image', b.business_name, b.business_image.name))
        if b.business_logo and b.business_logo.name:
            targets.append(('Business.logo', b.business_name, b.business_logo.name))
    
    # Check Category images
    for c in Category.objects.all():
        if c.image and c.image.name:
            targets.append(('Category', c.name, c.image.name))
    
    # Check Product images
    for prod in Product.objects.all():
        for field_name in ['product_image', 'product_image1', 'product_image2', 'product_image3', 'product_image4']:
            img = getattr(prod, field_name, None)
            if img and img.name:
                targets.append((f'Product.{field_name}', prod.product_name, img.name))
    
    uploaded_count = 0
    missing_count = 0
    
    for kind, owner, public_id in targets:
        if not public_id:
            continue
        
        # Check if file already exists in Cloudinary
        try:
            cloudinary_api.resource(public_id)
            print(f"  [EXISTS] {kind} ({owner}): {public_id}")
            continue
        except Exception:
            pass
        
        # Try to upload from local file
        local_file = MEDIA_ROOT / public_id
        if local_file.exists():
            try:
                uploader.upload(
                    str(local_file),
                    public_id=public_id,
                    resource_type='image',
                    overwrite=True,
                    use_filename=False,
                    unique_filename=False
                )
                print(f"  [UPLOADED] {kind} ({owner}): {public_id}")
                uploaded_count += 1
            except Exception as e:
                print(f"  [FAILED] {kind} ({owner}): {public_id} - {e}")
                missing_count += 1
        else:
            print(f"  [MISSING] {kind} ({owner}): {public_id} (local file not found)")
            missing_count += 1
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)
    print(f"\nDeleted {len(malformed_files)} malformed files")
    print(f"Re-uploaded {uploaded_count} files from local media")
    print(f"Missing files (need re-upload through app): {missing_count}")
    
    if missing_count > 0:
        print("\n[NOTE] Some images could not be re-uploaded because local files are missing.")
        print("       Please re-upload these images through the Django admin or app.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
