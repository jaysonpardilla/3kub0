import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from products.views import add_category
from products.forms import AddCategory
from products.models import Category

def test_add_category():
    # Create a mock request
    factory = RequestFactory()

    # Create a test user
    try:
        user = User.objects.create_user(username='testuser', password='testpass')
    except:
        user = User.objects.get(username='testuser')

    # Create POST data
    data = {
        'name': 'Test Category'
    }

    # Create a simple image file for testing
    from io import BytesIO
    from PIL import Image

    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    files = {
        'image': image_buffer
    }

    # Create the request
    request = factory.post('/add-category/', data=data, files=files)
    request.user = user

    # Add session and messages middleware
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    messages_middleware = AuthenticationMiddleware()
    messages_middleware.process_request(request)

    # Mock messages
    from django.contrib import messages
    request._messages = default_storage(request)

    try:
        # Call the view
        response = add_category(request)

        # Check if category was created
        category = Category.objects.filter(name='Test Category').first()
        if category:
            print(f"✓ Category created successfully: {category.name}")
            print(f"✓ Image field: {category.image}")
        else:
            print("✗ Category was not created")

        # Check response
        if hasattr(response, 'status_code'):
            print(f"✓ Response status: {response.status_code}")
        else:
            print("✓ View returned a response (likely redirect)")

    except Exception as e:
        print(f"✗ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_add_category()
