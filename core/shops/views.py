from django.shortcuts import render, redirect, get_object_or_404
from products.models import Business
from products.forms import UpdateBusinessForm
from django.urls import reverse
from products.models import Product
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from products.models import Category
from cloudinary import uploader
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@login_required(login_url='/login/')
def shops_list(request):
    shop = Business.objects.filter(business_name__isnull=False) | Business.objects.filter(business_name__isnull=False)
    total_shop = shop.count()
    
    context = {'shop':shop,'total_shop':total_shop}
    return render(request, 'shops/shop_list.html', context)

@login_required(login_url='/login/')
def update_shop(request, pk):
    instance = get_object_or_404(Business, pk=pk)
    if request.method == 'POST':
        form = UpdateBusinessForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            business = form.save(commit=False)
            
            # Handle business_image upload - ensure only public_id is stored
            if 'business_image' in request.FILES:
                image_file = request.FILES['business_image']
                try:
                    # Upload to Cloudinary and get only the public_id
                    result = uploader.upload(
                        image_file,
                        folder='business_image',
                        resource_type='image'
                    )
                    # Store only the public_id (relative path), not the full URL
                    business.business_image = result.get('public_id', '')
                except Exception as e:
                    logger.error(f"Error uploading business_image: {e}")
            
            # Handle business_logo upload - ensure only public_id is stored
            if 'business_logo' in request.FILES:
                logo_file = request.FILES['business_logo']
                try:
                    # Upload to Cloudinary and get only the public_id
                    result = uploader.upload(
                        logo_file,
                        folder='business_logo',
                        resource_type='image'
                    )
                    # Store only the public_id (relative path), not the full URL
                    business.business_logo = result.get('public_id', '')
                except Exception as e:
                    logger.error(f"Error uploading business_logo: {e}")
            
            business.save()
            return redirect(reverse('chat:profile_detail'))
    else:
        form = UpdateBusinessForm(instance=instance)
    return render(request, 'shops/update-shop.html', {'form': form})

@login_required(login_url='/login/')
def view_shop(request, pk):
    shop = get_object_or_404(Business, pk=pk)
    products = Product.objects.filter(seller=shop)
    total_products = products.count()
    user = request.user
    query = request.GET.get('q', '')
    results = Product.objects.filter(product_name__icontains=query) if query else []

    context = {
        'shop': shop,
        'product': products,
        'total_product': total_products,
        'user': user,
        'query':query,
        'results':results,
    }
    return render(request, 'shops/view-shop.html', context)








