#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from products.models import Product

with open('db_status.txt', 'w') as f:
    count = Product.objects.count()
    f.write(f'Total products: {count}\n\n')
    
    for prod in Product.objects.all()[:10]:
        f.write(f'- {prod.product_name}\n')
        for field_name in ['product_image', 'product_image1', 'product_image2', 'product_image3', 'product_image4']:
            img = getattr(prod, field_name)
            if img:
                name = getattr(img, 'name', '(no name)')
                f.write(f'    {field_name}: {name}\n')
