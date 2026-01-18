from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')), 
    path('products/', include('products.urls')),
    path('manage-business/', include('manage_business.urls')),
    path('shops/', include('shops.urls'))
]

# Static files are served by WhiteNoise middleware in production
# Serve static files in development only
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






