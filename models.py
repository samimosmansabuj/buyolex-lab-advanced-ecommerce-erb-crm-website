
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.text import slugify
import uuid

try:
    # Django 3.1+
    from django.db.models import JSONField
except Exception:
    # Fallback for older versions
    from django.contrib.postgres.fields import JSONField


# ----------------------------
# common / core utilities
# ----------------------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ----------------------------
# accounts app
# ----------------------------
class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('branch_staff', 'Branch staff'),
        ('vendor_admin', 'Vendor admin'),
        ('admin', 'Admin'),
        ('super_admin', 'Super admin'),
    ]

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='customer')
    profile_photo = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    metadata = JSONField(default=dict, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Branch(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    vendor = models.ForeignKey('vendors.Vendor', related_name='branches', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True)
    address = JSONField(default=dict, blank=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    opening_hours = JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.name}"


class Staff(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='staff')
    designation = models.CharField(max_length=255, blank=True)
    permissions = JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} @ {self.branch.name}"


# ----------------------------
# roles app (optional granular permissions)
# ----------------------------
class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module_name = models.CharField(max_length=128)
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module_name')


# ----------------------------
# vendors app
# ----------------------------
class Vendor(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    legal_info = JSONField(default=dict, blank=True)
    contact = JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class VendorStaff(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    role = models.CharField(max_length=128, blank=True)
    permissions = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vendor')


# ----------------------------
# catalog app (categories, products, attributes, variants, media)
# ----------------------------
class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    icon = models.URLField(blank=True, null=True)
    banner_image = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='active')
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Brand(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('dropdown', 'Dropdown'),
        ('color', 'Color'),
        ('swatch', 'Swatch'),
    ]
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='text')
    is_variant = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    id = models.BigAutoField(primary_key=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=255)
    hex_code = models.CharField(max_length=20, blank=True, null=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = (('attribute', 'value'),)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(TimeStampedModel):
    PRODUCT_TYPE = [
        ('simple', 'Simple'),
        ('variable', 'Variable'),
        ('digital', 'Digital'),
        ('service', 'Service'),
    ]

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, unique=True, blank=True, null=True)
    sku = models.CharField(max_length=128, blank=True, null=True)
    barcode = models.CharField(max_length=128, blank=True, null=True)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPE, default='simple')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL)
    short_description = models.TextField(blank=True, null=True)
    description_html = models.TextField(blank=True, null=True)
    description_json = JSONField(default=list, blank=True)  # blocks for landing page builder
    featured_image = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    landing_page = models.ForeignKey('landing_pages.LandingPage', null=True, blank=True, on_delete=models.SET_NULL)
    seo = JSONField(default=dict, blank=True)
    tags = JSONField(default=list, blank=True)  # simple list
    status = models.CharField(max_length=50, default='draft')
    metadata = JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            self.slug = f"{base}-{str(self.uuid)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductVariant(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=128, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=128, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    inventory_policy = models.CharField(max_length=50, default='deny')  # deny or continue
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = JSONField(default=dict, blank=True)
    attributes = JSONField(default=dict, blank=True)  # {"size":"M","color":"red"}
    images = JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.sku or self.id}"


class ProductMedia(models.Model):
    MEDIA_TYPE = [('image', 'Image'), ('video', 'Video')]
    ROLE = [('primary', 'Primary'), ('gallery', 'Gallery'), ('attribute', 'Attribute'), ('hero', 'Hero')]

    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE, related_name='media')
    url = models.URLField()
    type = models.CharField(max_length=20, choices=MEDIA_TYPE, default='image')
    role = models.CharField(max_length=20, choices=ROLE, default='gallery')
    metadata = JSONField(default=dict, blank=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"Media {self.id} for {self.product.title}"


# ----------------------------
# inventory app
# ----------------------------
class Warehouse(models.Model):
    id = models.BigAutoField(primary_key=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = JSONField(default=dict, blank=True)
    lead_time_days = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class InventoryLevel(models.Model):
    id = models.BigAutoField(primary_key=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='inventory_levels')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_levels')
    available = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    incoming = models.IntegerField(default=0)

    class Meta:
        unique_together = ('variant', 'warehouse')

    def __str__(self):
        return f"{self.variant} @ {self.warehouse}"


class StockMovement(models.Model):
    REASON_CHOICES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('transfer', 'Transfer'),
    ]
    id = models.BigAutoField(primary_key=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    delta = models.IntegerField()
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reference_type = models.CharField(max_length=128, blank=True, null=True)
    reference_id = models.CharField(max_length=128, blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.delta} {self.variant} @ {self.warehouse}"


# ----------------------------
# cart & orders app
# ----------------------------
class Cart(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    items = JSONField(default=list, blank=True)  # quick store, but normalize with CartItem if needed
    totals = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} - {self.user or self.token}"


class CartItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_snapshot = JSONField(default=dict)  # price at time of adding
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f"{self.quantity}x {self.variant} in cart {self.cart.id}"


class Order(TimeStampedModel):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('paid', 'Paid'),
        ('partially_shipped', 'Partially shipped'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    ]

    id = models.BigAutoField(primary_key=True)
    order_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_number = models.CharField(max_length=128, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)

    currency = models.CharField(max_length=3, default='USD')
    items_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=50, default='pending')
    payment_method = JSONField(default=dict, blank=True)  # provider snapshot

    order_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    billing_address = JSONField(default=dict, blank=True)
    shipping_address = JSONField(default=dict, blank=True)
    promotions_applied = JSONField(default=list, blank=True)
    metadata = JSONField(default=dict, blank=True)
    placed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # simple example order number
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{str(self.order_uuid)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    product_snapshot = JSONField(default=dict, blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fulfillment_status = models.CharField(max_length=50, default='pending')
    warehouse = models.ForeignKey(Warehouse, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.quantity} x {self.product}"


class Shipment(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    shipment_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    carrier = models.CharField(max_length=255, blank=True, null=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    items = JSONField(default=list, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    label_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Shipment {self.shipment_uuid} for {self.order.order_number}"


class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    provider = models.CharField(max_length=128)  # e.g., stripe, bkash
    provider_reference = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=50, default='pending')
    raw_response = JSONField(default=dict, blank=True)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_uuid} ({self.provider})"


class Refund(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)
    metadata = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Refund {self.id} for {self.order.order_number}"


# ----------------------------
# offers app
# ----------------------------
class OfferTemplate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    template_json = JSONField(default=dict, blank=True)
    default_content = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Offer(models.Model):
    TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed_cart', 'Fixed cart'),
        ('fixed_item', 'Fixed item'),
        ('buy_x_get_y', 'Buy X get Y'),
        ('bundle', 'Bundle'),
        ('combo', 'Combo'),
    ]
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL)
    template = models.ForeignKey(OfferTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    conditions = JSONField(default=dict, blank=True)
    actions = JSONField(default=dict, blank=True)
    priority = models.IntegerField(default=0)
    usage_limit = models.IntegerField(null=True, blank=True)
    per_customer_limit = models.IntegerField(null=True, blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='draft')
    short_link = models.ForeignKey('shortener.ShortLink', null=True, blank=True, on_delete=models.SET_NULL)
    metadata = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class OfferUsage(models.Model):
    id = models.BigAutoField(primary_key=True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    amount_saved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usage of {self.offer.name} on {self.order.order_number}"


class Coupon(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=64, unique=True)
    offer = models.ForeignKey(Offer, null=True, blank=True, on_delete=models.SET_NULL)
    usage_count = models.IntegerField(default=0)
    max_uses = models.IntegerField(null=True, blank=True)
    min_purchase = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


# ----------------------------
# landing_pages app
# ----------------------------
class LandingPage(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    featured_image = models.URLField(blank=True, null=True)
    seo = JSONField(default=dict, blank=True)
    content_builder = JSONField(default=list, blank=True)  # list of blocks
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ----------------------------
# shortener app
# ----------------------------
class ShortLink(models.Model):
    id = models.BigAutoField(primary_key=True)
    original_url = models.TextField()
    short_code = models.CharField(max_length=64, unique=True)
    click_count = models.BigIntegerField(default=0)
    metadata = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_code


# ----------------------------
# marketing app
# ----------------------------
class MarketingIntegration(models.Model):
    PROVIDER_CHOICES = [
        ('facebook_pixel', 'Facebook Pixel'),
        ('facebook_capi', 'Facebook Conversion API'),
        ('gtm', 'Google Tag Manager'),
        ('ga4', 'Google Analytics 4'),
    ]
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE)
    provider = models.CharField(max_length=64, choices=PROVIDER_CHOICES)
    config = JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, default='inactive')
    last_tested_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} ({self.vendor or 'global'})"


class MarketingEventLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=255)
    payload = JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    response = JSONField(default=dict, blank=True)
    status = models.CharField(max_length=64, default='pending')
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_name} for {self.vendor}"


# ----------------------------
# reviews app
# ----------------------------
class Review(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    photos = JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars — {self.product}"


# ----------------------------
# notifications app
# ----------------------------
class Notification(models.Model):
    TYPE_CHOICES = [('email', 'Email'), ('sms', 'SMS'), ('push', 'Push')]
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='email')
    data = JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"


# ----------------------------
# settings_app
# ----------------------------
class SiteSettings(models.Model):
    id = models.BigAutoField(primary_key=True)
    site_name = models.CharField(max_length=255, default='My Marketplace')
    logo = models.URLField(blank=True, null=True)
    favicon = models.URLField(blank=True, null=True)
    primary_color = models.CharField(max_length=20, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=64, default='UTC')
    email_settings = JSONField(default=dict, blank=True)
    sms_settings = JSONField(default=dict, blank=True)
    payment_gateways = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.site_name


# ----------------------------
# optional analytics / search queue
# ----------------------------
class SearchIndexQueue(models.Model):
    id = models.BigAutoField(primary_key=True)
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=128)
    action = models.CharField(max_length=32, default='index')
    payload = JSONField(default=dict, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} -> {self.action}"


# End of file
