from django.urls import path
from .views import product_landing_page, CreateOrderView, get_order
from .api_views import *

urlpatterns = [
    path('', product_landing_page, name="product_landing_page"),
    path('order/create-order/', CreateOrderView.as_view(), name="create_order"),

    path('order/<int:id>/', get_order, name="get_order"),

    path('api/product/', LandingPageProductAPIView.as_view(), name="LandingPageProductAPIView"),
    path('api/order-create/', LandingPageOrderAPIView.as_view(), name="LandingPageOrderAPIView"),
]
