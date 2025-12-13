from django.urls import path
from .views import product_landing_page, CreateOrderView, get_order

urlpatterns = [
    # path('', product_landing_page, name="product_landing_page"),
    path('order/create-order/', CreateOrderView.as_view(), name="create_order"),

    path('order/<int:id>/', get_order, name="get_order")
]
