from django.contrib import admin
from .models import *

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Shipment)
admin.site.register(Payment)
admin.site.register(Refund)
admin.site.register(Review)
