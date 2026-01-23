from django.db import models
from .utix import *
from settings_app.utils import generate_unique_slug, image_delete_os, previous_image_delete_os
from .utils import generate_product_sku
import uuid
from settings_app.models import Tag

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    icon = models.CharField(max_length=10, blank=True, null=True)
    banner_image = models.ImageField(upload_to="category/banner/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=CATEGORY_STATUS.choices, default=CATEGORY_STATUS.ACTIVE)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        old_slug = Category.objects.get(pk=self.pk) if self.pk else None
        self.slug = generate_unique_slug(Category, self.name, old_slug.slug if old_slug else None)

        return super().save(*args, **kwargs)
    
    @property
    def get_category_path(self):
        path = []
        category = self
        while category:
            path.append(category)
            category = category.parent
        path_string = None
        for p in path:
            if path_string is None:
                path_string = f"{p.name}"
            else:
                path_string += f" -> {p.name}"
        # return list(reversed(path))
        return path_string

    def __str__(self):
        return self.name

class Brand(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    logo = models.ImageField(upload_to="brand/logo/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        old_slug = Brand.objects.get(pk=self.pk) if self.pk else None
        self.slug = generate_unique_slug(Brand, self.name, old_slug.slug if old_slug else None)
        
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    type = models.CharField(max_length=50, choices=ATTRIBUTE_TYPE.choices, default=ATTRIBUTE_TYPE.TEXT)
    is_variant = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        old_slug = Attribute.objects.get(pk=self.pk) if self.pk else None
        self.slug = generate_unique_slug(Attribute, self.name, old_slug.slug if old_slug else None)

        super().save(*args, **kwargs)

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
    # price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL)
    short_description = models.TextField(blank=True, null=True)
    description_html = models.TextField(blank=True, null=True)
    description_json = models.JSONField(default=list, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)

    # landing_page = models.ForeignKey('landing_pages.LandingPage', null=True, blank=True, on_delete=models.SET_NULL)
    seo = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)  # simple list
    status = models.CharField(max_length=50, choices=PRODUCT_STATUS.choices, default=PRODUCT_STATUS.DRAFT)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def active_variante(self):
        return self.variants.filter(is_active=True)
    
    @property
    def category_path(self):
        if not self.category:
            return []
        return self.category.get_category_path
    
    @property
    def primary_image(self):
        primary_image = self.images.filter(role=PRODUCT_MEDIA_ROLE.PRIMARY).first()
        if primary_image:
            return primary_image.image.url
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return None


    def save(self, *args, **kwargs):
        old_slug = Category.objects.get(pk=self.pk) if self.pk else None
        self.slug = generate_unique_slug(Category, self.title, old_slug.slug if old_slug else None)
        if not self.sku:
            self.sku = generate_product_sku()
        if not self.uuid:
            self.uuid = uuid.uuid4().hex

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# class SingleProduct(models.Model):
#     product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='single_price')
#     price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     discount_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#     cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
#     inventory_quantity = models.IntegerField(default=0)
#     weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
#     dimensions = models.JSONField(default=dict, blank=True)

#     def __str__(self) -> str:
#         return f"Item details of {self.product.title}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=128, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=128, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    inventory_quantity = models.IntegerField(default=0)
    # inventory_policy = models.CharField(max_length=50, default='deny')  # deny or continue
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)
    attributes = models.JSONField(default=dict, blank=True)  # {"size":"M","color":"red"}

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['sku']), ]
        unique_together = (('product', 'sku'),)
    
    def get_product_sku(self):
        self.sku = f"{self.product.sku}"
        for key, value in self.attributes.items():
            self.sku = f"{self.sku}-{value}"
        return True
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.get_product_sku()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.title} - {self.sku or self.pk}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="product/images/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=PRODUCT_MEDIA_ROLE, default=PRODUCT_MEDIA_ROLE.GALLERY)
    metadata = models.JSONField(default=dict, blank=True)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        image_delete_os(self.image)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        old_instance = ProductImage.objects.get(pk=self.pk) if self.pk else None
        if old_instance:
            previous_image_delete_os(old_instance.image, self.image)
        
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"Image {self.pk} for {self.product.title}"

class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to="product/videos/", blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        image_delete_os(self.video)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        old_instance = ProductVideo.objects.get(pk=self.pk) if self.pk else None
        if old_instance:
            previous_image_delete_os(old_instance.video, self.video)
        
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"Video {self.pk} for {self.product.title}"

class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='product_tags')

    def __str__(self):
        return f"Tag {self.tag.name} for {self.product.title}"


