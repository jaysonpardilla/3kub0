from django.urls import path, re_path
from . import consumers

# WebSocket URL routing for Django Channels
# Handles chat WebSocket connections
websocket_urlpatterns = [
    path('ws/chat/<uuid:user_id>/', consumers.ChatConsumer.as_asgi()),
]
