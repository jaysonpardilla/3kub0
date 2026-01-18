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

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None

BASE_DIR = Path(settings.BASE_DIR)
MEDIA_ROOT = BASE_DIR / 'media'
TMP_DIR = BASE_DIR / 'tmp_upload_placeholders'
TMP_DIR.mkdir(exist_ok=True)

def resource_exists(public_id):
    if not public_id:
        return False
    try:
        cloudinary_api.resource(public_id)
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
            ,upload_preset=getattr(settings, 'CLOUDINARY_UPLOAD_PRESET', None)
        )
        return True, result
    except Exception as e:
        return False, str(e)

# Build targets
targets = []
for p in Profile.objects.all():
    pid = p.profile.name if p.profile and getattr(p.profile, 'name', None) else ''
    if pid:
        targets.append(('Profile', p.user.username if p.user else str(p.id), pid))
for b in Business.objects.all():
    if b.business_image and b.business_image.name:
        targets.append(('Business.image', b.business_name, b.business_image.name))
    if b.business_logo and b.business_logo.name:
        targets.append(('Business.logo', b.business_name, b.business_logo.name))
for c in Category.objects.all():
    if c.image and c.image.name:
        targets.append(('Category', c.name, c.image.name))
for prod in Product.objects.all():
    for fld, name in [('Product.main', prod.product_image.name if prod.product_image else ''),
                      ('Product.1', prod.product_image1.name if prod.product_image1 else ''),
                      ('Product.2', prod.product_image2.name if prod.product_image2 else ''),
                      ('Product.3', prod.product_image3.name if prod.product_image3 else ''),
                      ('Product.4', prod.product_image4.name if prod.product_image4 else '')]:
        if name:
            targets.append((fld, prod.product_name, name))

print('='*80)
print('UPLOAD PLACEHOLDERS FOR MISSING CLOUDINARY FILES')
print('='*80)

for kind, owner, public_id in targets:
    if not public_id:
        continue
    print(f"\nProcessing {kind} ({owner}): {public_id}")
    if resource_exists(public_id):
        print('  Already exists on Cloudinary')
        continue
    local_file = MEDIA_ROOT / public_id
    if local_file.exists():
        print(f'  Local file found: {local_file} — uploading')
        ok, res = upload_file(local_file, public_id)
        print('  Uploaded' if ok else f'  Upload failed: {res}')
        continue
    # No local file — create placeholder image
    placeholder_path = TMP_DIR / (public_id.replace('/', '_') + '.png')
    placeholder_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if Image is None:
            # Create a tiny 1x1 PNG via bytes fallback
            with open(placeholder_path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\x99c``\x00\x00\x00\x04\x00\x01\x0c\n\x02\xfe\xa2\x00\x00\x00\x00IEND\xaeB`\x82')
        else:
            img = Image.new('RGB', (400, 300), color=(200,200,200))
            d = ImageDraw.Draw(img)
            text = owner if owner else 'Image'
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
            d.text((10,140), text, fill=(50,50,50), font=font)
            img.save(placeholder_path)
        print(f'  Created placeholder at {placeholder_path}')
        ok, res = upload_file(placeholder_path, public_id)
        if ok:
            print('  Placeholder uploaded to Cloudinary ✅')
        else:
            print(f'  Upload failed: {res}')
    except Exception as e:
        print(f'  Failed to create/upload placeholder: {e}')

print('\nDone')
