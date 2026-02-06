#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from products.models import Product

fixed = 0
for prod in Product.objects.all():
    for field_name in ['product_image', 'product_image1', 'product_image2', 'product_image3', 'product_image4']:
        img = getattr(prod, field_name)
        if img:
            name = getattr(img, 'name', '')
            if name and 'res.cloudinary.com' in name:
                with open('fix_log.txt', 'a') as f:
                    f.write(f'Found malformed URL in {prod.product_name}.{field_name}: {name}\n')
                setattr(prod, field_name, None)
                prod.save()
                fixed += 1
                with open('fix_log.txt', 'a') as f:
                    f.write(f'  Cleared {field_name}\n')

with open('fix_log.txt', 'a') as f:
    f.write(f'Total fixed: {fixed}\n')
