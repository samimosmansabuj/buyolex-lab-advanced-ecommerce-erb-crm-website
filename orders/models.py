from django.db import models
from accounts.models import CustomUser
from catalog.models import Product, ProductVariant
from .utix import *

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True, editable=False)
    items = models.JSONField(default=list, blank=True)  # quick store, but normalize with CartItem if needed
    totals = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.pk} - {self.user or self.token}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f"{self.quantity}x {self.variant} in cart {self.cart.pk}"









class Order(models.Model):
    # order_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_number = models.CharField(max_length=128, unique=True, blank=True, null=True)
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)

    # currency = models.CharField(max_length=3, default='USD')
    items_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=50, default='pending')
    payment_method = models.JSONField(default=dict, blank=True)  # provider snapshot

    order_status = models.CharField(max_length=50, choices=ORDER_STATUS.choices, default=ORDER_STATUS.NEW)
    billing_address = models.JSONField(default=dict, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)
    promotions_applied = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    placed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # if not self.order_number:
        #     # simple example order number
        #     self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{str(self.order_uuid)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    product_snapshot = models.JSONField(default=dict, blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fulfillment_status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"{self.quantity} x {self.product}"

class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    # shipment_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    carrier = models.CharField(max_length=255, blank=True, null=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    items = models.JSONField(default=list, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    label_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Shipment {self.carrier} for {self.order.order_number}"


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    # payment_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    provider = models.CharField(max_length=128)  # e.g., stripe, bkash
    provider_reference = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=50, default='pending')
    raw_response = models.JSONField(default=dict, blank=True)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.pk} ({self.provider})"


class Refund(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Refund {self.id} for {self.order.order_number}"