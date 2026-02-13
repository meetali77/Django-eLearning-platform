from django.urls import path
from .consumers import CourseChatConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:course_id>/", CourseChatConsumer.as_asgi()),
]