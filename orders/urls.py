from django.urls import path
from .api_views import DeliveryOptionListAPIView, OrderDeliveryOptionSubmitView, ShipmentInfoAPIView

urlpatterns = [
    path('api/v1/delivery-options/', DeliveryOptionListAPIView.as_view(), name="delivery-options"),
    path('api/v1/shipment-info/<int:order_id>/', ShipmentInfoAPIView.as_view(), name="shipment-info"),
    path('api/v1/orders/delivery-option-submit/<int:pk>/', OrderDeliveryOptionSubmitView.as_view(), name='order_delivery_option_submit'),
]
