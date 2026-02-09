from django.db import models

class ORDER_STATUS(models.TextChoices):
    NEW = "new"
    FOLLOW_UP = "follow_up"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"

class ORDER_PAYMENT_STATUS(models.TextChoices):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUND_PROCESSING = "refund_processing"
    REFUND = "refund"


class REVIEW_STATUS(models.TextChoices):
    PENDING = "pending"
    APPROVED = "approved"
    DELETE = "delete"


class DELIVERY_TYPE(models.TextChoices):
    COD = "COD"
    ONLINE_PAYMENT = "online_payment"
    DELIVERY = "delivery"
    PICKUP = "pickup"


class LOGISTIC_SERVICE_PROVIDER(models.TextChoices):
    PATHAO = "PATHAO"
    REDX = "REDX"
    STEADFAST = "STEADFAST"


