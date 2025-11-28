from django.urls import path
from django.conf.urls import handler500
from .views import custom_404_view

handler500 = custom_404_view

urlpatterns = [
    
]
