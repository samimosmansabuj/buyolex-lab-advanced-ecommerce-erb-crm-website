from django.urls import path
from .views import api_welcome_message

urlpatterns = [
    path("", api_welcome_message, name="api_welcome_message")
]
