from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import uuid
from django.utils import timezone
from django.db.models import Sum



class Business(models.Model):
    """
    Business model storing business information and images.
    
    IMPORTANT: Cloudinary URL Handling
    =================================
    This model stores only the public_id (relative path) for images.
    The business_image_url and business_logo_url properties construct
    the full Cloudinary URL on-demand using build_cloudinary_url.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_description = models.CharField(max_length=255)
    business_contact_number = models.CharField(max_length=255, blank=True)
    business_address = models.CharField(max_length=255, blank=True)
    business_image = models.ImageField(upload_to='business_image/', blank=True, null=True, max_length=500)
    business_logo = models.ImageField(upload_to='business_logo/', blank=True, null=True, max_length=500)
    business_created = models.DateTimeField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def business_image_url(self):
        """
        Generate the full Cloudinary URL for the business image.
        Handles both public_id and legacy full URL formats.
        """
        try:
            # Get the stored value (should be public_id, but might be full URL)
            stored_value = self.business_image.name if self.business_image else None
            if not stored_value:
                return ''
            
            # If it's already a full URL, extract the public_id
            if stored_value.startswith('http'):
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                return build_cloudinary_url(stored_value, cloud_name=cloud_name)
            
            # Otherwise, construct URL from public_id
            from django.conf import settings
            cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
            # Clean the public_id - remove any leading slashes or version prefixes
            public_id = stored_value.lstrip('/')
            import re
            public_id = re.sub(r'^v\d+/', '', public_id)
            
            # Determine extension
            if '.' in public_id:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
            else:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.png"
        except Exception:
            pass
        return ''

    @property
    def business_logo_url(self):
        """
        Generate the full Cloudinary URL for the business logo.
        Handles both public_id and legacy full URL formats.
        """
        try:
            # Get the stored value (should be public_id, but might be full URL)
            stored_value = self.business_logo.name if self.business_logo else None
            if not stored_value:
                return ''
            
            # If it's already a full URL, extract the public_id
            if stored_value.startswith('http'):
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                return build_cloudinary_url(stored_value, cloud_name=cloud_name)
            
            # Otherwise, construct URL from public_id
            from django.conf import settings
            cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
            # Clean the public_id - remove any leading slashes or version prefixes
            public_id = stored_value.lstrip('/')
            import re
            public_id = re.sub(r'^v\d+/', '', public_id)
            
            # Determine extension
            if '.' in public_id:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
            else:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.png"
        except Exception:
            pass
        return ''

    def __str__(self):
        return self.business_name

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    order_quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected")
    ], default="Pending")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order by {self.buyer} - Status: {self.status}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    quantity = models.IntegerField(default=1)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['created_at']

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')  # To prevent duplicate entries

class Category(models.Model):
    """
    Product category model.
    
    IMPORTANT: Cloudinary URL Handling
    =================================
    When storing image paths, NEVER store a full Cloudinary URL as the public_id.
    See Product model for details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='product_category/', blank=True, null=True, max_length=500)

    def __str__(self):
        return self.name
    
    def category_image_url(self):
        try:
            url = self.image.url
            if url:
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                return build_cloudinary_url(url, cloud_name=cloud_name)
        except:
            pass
        return ''

# Modify the Product Model to Add Method for Sales Reporting
class Product(models.Model):
    """
    IMPORTANT: Cloudinary URL Handling
    =================================
    When storing image paths, NEVER store a full Cloudinary URL as the public_id.
    Doing so causes 404 errors because Cloudinary treats the URL string as the filename.
    
    WRONG: https://res.cloudinary.com/deyrmzn1x/image/upload/product_images/bg_image.png
    RIGHT: product_images/bg_image.png
    
    The model properties like product_image_url() use build_cloudinary_url() to
    construct the full URL from the stored public_id for display.
    """
    MEASUREMENT_CHOICES = [
        ('Kilo', 'Per Kilo'),
        ('Gram', 'Per Gram'),
        ('Kiece', 'Per Piece'),
        ('Pack', 'Per Pack'),
        ('Liter', 'Per Liter')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    product_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')  # Category field added
    product_name = models.CharField(max_length=255)
    product_measurement = models.CharField(
        max_length=10,
        choices=MEASUREMENT_CHOICES,
        default='Per Kilo'
    )
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_stock = models.PositiveIntegerField()
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True, max_length=500)
    product_image1 = models.ImageField(upload_to='product_images/', blank=True, null=True, max_length=500)
    product_image2 = models.ImageField(upload_to='product_images/', blank=True, null=True, max_length=500)
    product_image3 = models.ImageField(upload_to='product_images/', blank=True, null=True, max_length=500)
    product_image4 = models.ImageField(upload_to='product_images/', blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(default=timezone.now)


    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0  # If no reviews exist, return 0
    

    def product_image_url(self):
        try:
            url = self.product_image.url
            if url:
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                result = build_cloudinary_url(url, cloud_name=cloud_name)
                print(f"DEBUG product_image_url: input='{url}', output='{result}'")
                return result
        except Exception as e:
            print(f"DEBUG product_image_url ERROR: {e}, url='{url if 'url' in locals() else 'N/A'}'")
        return ''
    
    def product1_image_url(self):
        try:
            url = self.product_image1.url
            if url:
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                return build_cloudinary_url(url, cloud_name=cloud_name)
        except:
            pass
        return ''
    
    def product2_image_url(self):
        try:
            url = self.product_image2.url
            if url:
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                return build_cloudinary_url(url, cloud_name=cloud_name)
        except:
            pass
        return ''
    
    def product3_image_url(self):
        try:
            url = self.product_image3.url
            if url:
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                return build_cloudinary_url(url, cloud_name=cloud_name)
        except:
            pass
        return ''
    
    def product4_image_url(self):
        try:
            url = self.product_image4.url
            if url:
                from products.utils import build_cloudinary_url
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')
                return build_cloudinary_url(url, cloud_name=cloud_name)
        except:
            pass
        return ''

    def __str__(self):
        return self.product_name



class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)]) 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together = ('product', 'user')  

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.product_name}'


class SellerReport(models.Model):
    buyer_name = models.CharField(max_length=100)
    buyer_email = models.EmailField()
    seller_name = models.CharField(max_length=100)
    shop_name = models.CharField(max_length=100)
    message = models.TextField()
    evidence_image = models.ImageField(upload_to='evidence_images/', max_length=500)
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.buyer_name} - {self.shop_name} report"





