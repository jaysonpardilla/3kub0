#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from cloudinary import uploader, api as cloudinary_api
from chat.models import Profile
from products.models import Product, Category, Business

BASE_DIR = Path(settings.BASE_DIR)
MEDIA_ROOT = BASE_DIR / 'media'

def resource_exists(public_id):
    if not public_id:
        return False
    try:
        res = cloudinary_api.resource(public_id)
        return True
    except Exception:
        return False

def upload_file(local_path, public_id):
    try:
        result = uploader.upload(
            str(local_path),
            public_id=public_id,
            resource_type='image',
            overwrite=True,
            use_filename=False,
            unique_filename=False
        )
        return True, result
    except Exception as e:
        return False, str(e)

summary = []

# Collect targets
targets = []

# Profiles
for p in Profile.objects.all():
    public_id = p.profile.name if p.profile and getattr(p.profile, 'name', None) else ''
    targets.append(('Profile', p.user.username if p.user else str(p.id), public_id))

# Businesses
for b in Business.objects.all():
    targets.append(('Business.image', b.business_name, b.business_image.name if b.business_image else ''))
    targets.append(('Business.logo', b.business_name, b.business_logo.name if b.business_logo else ''))

# Categories
for c in Category.objects.all():
    targets.append(('Category', c.name, c.image.name if c.image else ''))

# Products
for prod in Product.objects.all():
    targets.append(('Product.main', prod.product_name, prod.product_image.name if prod.product_image else ''))
    targets.append(('Product.1', prod.product_name, prod.product_image1.name if prod.product_image1 else ''))
    targets.append(('Product.2', prod.product_name, prod.product_image2.name if prod.product_image2 else ''))
    targets.append(('Product.3', prod.product_name, prod.product_image3.name if prod.product_image3 else ''))
    targets.append(('Product.4', prod.product_name, prod.product_image4.name if prod.product_image4 else ''))

# Process targets
print('='*80)
print('UPLOAD MISSING MEDIA TO CLOUDINARY')
print('='*80)

for model_name, owner, public_id in targets:
    if not public_id:
        continue
    print(f"\nChecking {model_name} ({owner}): {public_id}")
    if resource_exists(public_id):
        print('  Exists on Cloudinary — skipping')
        summary.append((model_name, owner, public_id, 'exists'))
        continue
    # Try local file
    local_file = MEDIA_ROOT / public_id
    if local_file.exists():
        print(f'  Found local file: {local_file}')
        ok, res = upload_file(local_file, public_id)
        if ok:
            print('  Uploaded to Cloudinary ✅')
            summary.append((model_name, owner, public_id, 'uploaded'))
        else:
            print(f'  Upload failed: {res}')
            summary.append((model_name, owner, public_id, f'upload_failed: {res}'))
    else:
        print('  Local file not found — cannot upload')
        summary.append((model_name, owner, public_id, 'local_missing'))

print('\n' + '='*80)
print('SUMMARY:')
counts = {}
for item in summary:
    status = item[3]
    counts[status] = counts.get(status, 0) + 1
    print(f" - {item[0]} {item[1]}: {item[2]} -> {status}")
print('\nCounts:')
for k,v in counts.items():
    print(f"  {k}: {v}")
print('\nDone')
