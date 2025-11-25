from django.db import models

class USER_TYPE(models.TextChoices):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

