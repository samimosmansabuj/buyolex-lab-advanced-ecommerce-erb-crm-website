from django.urls import path
from .views import product_landing_page, CreateOrderView

urlpatterns = [
    path('', product_landing_page, name="product_landing_page"),
    path('order/create-order/', CreateOrderView.as_view(), name="create_order")
]
