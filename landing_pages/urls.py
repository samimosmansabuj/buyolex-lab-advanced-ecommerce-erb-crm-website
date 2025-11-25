from django.urls import path
from .views import product_landing_page

urlpatterns = [
    path('', product_landing_page, name="product_landing_page")
]
