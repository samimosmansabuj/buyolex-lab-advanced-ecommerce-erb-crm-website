from django.db import models
from .utix import *
from django.utils.text import slugify

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
    status = models.CharField(max_length=50, choices=CATEGORY_STATUS.choices, default=CATEGORY_STATUS.ACTIVE)
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
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    type = models.CharField(max_length=50, choices=ATTRIBUTE_TYPE.choices, default=ATTRIBUTE_TYPE.TEXT)
    is_variant = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=255)
    hex_code = models.CharField(max_length=20, blank=True, null=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = (('attribute', 'value'),)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"







class Product(models.Model):
    uuid = models.CharField(max_length=255, unique=True, editable=False)
    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, unique=True, blank=True, null=True)
    sku = models.CharField(max_length=128, blank=True, null=True)
    barcode = models.CharField(max_length=128, blank=True, null=True)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPE.choices, default=PRODUCT_TYPE.SIMPLE)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL)
    short_description = models.TextField(blank=True, null=True)
    description_html = models.TextField(blank=True, null=True)
    description_json = models.JSONField(default=list, blank=True)

    # featured_image = models.URLField(blank=True, null=True)
    # video_url = models.URLField(blank=True, null=True)
    # landing_page = models.ForeignKey('landing_pages.LandingPage', null=True, blank=True, on_delete=models.SET_NULL)
    seo = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)  # simple list
    status = models.CharField(max_length=50, choices=PRODUCT_STATUS.choices, default=PRODUCT_STATUS.DRAFT)
    metadata = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            self.slug = f"{base}-{str(self.uuid)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=128, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=128, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    inventory_policy = models.CharField(max_length=50, default='deny')  # deny or continue
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)
    attributes = models.JSONField(default=dict, blank=True)  # {"size":"M","color":"red"}

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.sku or self.pk}"

class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE, related_name='media')
    url = models.FileField(upload_to="product/", blank=True, null=True)
    type = models.CharField(max_length=20, choices=PRODUCT_MEDIA_TYPE.choices, default=PRODUCT_MEDIA_TYPE.IMAGE)
    role = models.CharField(max_length=20, choices=PRODUCT_MEDIA_ROLE, default=PRODUCT_MEDIA_ROLE.GALLERY)
    metadata = models.JSONField(default=dict, blank=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"Media {self.pk} for {self.product.title}"


