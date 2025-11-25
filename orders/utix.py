from django.db import models

class ORDER_STATUS(models.TextChoices):
    NEW = "new"
    PAID = "paid"
    PARTIAL = "partially_shipped"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"

