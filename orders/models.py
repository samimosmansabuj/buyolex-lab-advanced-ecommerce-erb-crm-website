from django.db import models
from accounts.models import CustomUser, CustomerProfile
from catalog.models import Product, ProductVariant
from .utix import *
import random, string
import uuid

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
    order_uuid = models.CharField(max_length=255, unique=True, editable=False)
    order_id = models.CharField(max_length=128, unique=True, blank=True, null=True)
    customer = models.ForeignKey(CustomerProfile, null=True, blank=True, on_delete=models.SET_NULL)

    # currency = models.CharField(max_length=3, default='USD')
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=50, choices=ORDER_PAYMENT_STATUS.choices, default=ORDER_PAYMENT_STATUS.PENDING)
    payment_method = models.JSONField(default=dict, blank=True)

    order_status = models.CharField(max_length=50, choices=ORDER_STATUS.choices, default=ORDER_STATUS.NEW)
    billing_address = models.JSONField(default=dict, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)
    promotions_applied = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_type = models.CharField(max_length=50, choices=DELIVERY_TYPE.choices, default=DELIVERY_TYPE.COD)

    @property
    def get_items_total(self):
        product_item = len(self.items.all())
        return product_item
    
    @property
    def get_total_quantity(self):
        total_quantity = sum(item.quantity for item in self.items.all())
        return total_quantity
        
    
    @property
    def get_discount_total(self):
        discount_total = sum(item.discount_total_price for item in self.items.all())
        return discount_total
    
    @property
    def get_current_total(self):
        current_total = sum(item.total_price for item in self.items.all())
        return current_total
    
    @property
    def get_discount_percentage(self):
        if not self.get_discount_total or self.get_discount_total >= self.get_current_total:
            return 0
        discount_amount = self.get_current_total - self.get_discount_total
        discount_percentage = (discount_amount / self.get_current_total) * 100
        return round(discount_percentage, 2)

    def generate_order_id(self):
        while True:
            prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
            suffix = ''.join(random.choices(string.digits, k=6))
            unique_id = prefix + suffix
            if not Order.objects.filter(order_id=unique_id).exists():
                return unique_id

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        if not self.order_uuid:
            self.order_uuid = uuid.uuid4().hex

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    product_snapshot = models.JSONField(default=dict, blank=True)
    quantity = models.IntegerField(default=1)

    c_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    d_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # fulfillment_status = models.CharField(max_length=50, default='pending')

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = float(self.c_unit_price) * self.quantity
        if not self.discount_total_price:
            self.discount_total_price = float(self.d_unit_price) * self.quantity
        
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product}"



class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    # shipment_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    courier = models.CharField(max_length=255, blank=True, null=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    items = models.JSONField(default=list, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    label_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Shipment {self.courier} for {self.order.order_id}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    # payment_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    provider = models.CharField(max_length=128)  # e.g., stripe, bkash
    provider_reference = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
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
        return f"Refund {self.id} for {self.order.order_id}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, related_name="order", blank=True, null=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=REVIEW_STATUS.choices, default=REVIEW_STATUS.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars — {self.product}"

