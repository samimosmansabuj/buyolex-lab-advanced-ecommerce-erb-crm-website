from django.db import models
from .utils import generate_unique_slug

# Create your models here.
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default='My Marketplace')
    site_slogan = models.CharField(max_length=255, blank=True, null=True)

    primary_logo = models.ImageField(upload_to="logo/", blank=True, null=True)
    secondary_logo = models.ImageField(upload_to="logo/", blank=True, null=True)
    intro_video = models.FileField(upload_to="intro-videos/", blank=True, null=True)
    favicon = models.ImageField(upload_to="logo/", blank=True, null=True)

    primary_color = models.CharField(max_length=20, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=64, default='UTC')

    payment_gateways = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name or "Site Settings"

class MainSlider(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="sliders/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title or 'Slider'} - {'Active' if self.is_active else 'Inactive'}"

class WhyBuyolex(models.Model):
    question = models.CharField(max_length=255, blank=True, null=True)
    header = models.TextField(blank=True, null=True)
    content = models.JSONField(default=list, blank=True)
    footer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.question or self.header}"

class DeliveryReturnPolicy(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    header = models.TextField(blank=True, null=True)
    content = models.JSONField(default=list, blank=True)
    footer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        old_slug = Tag.objects.get(pk=self.pk) if self.pk else None
        self.slug = generate_unique_slug(Tag, self.name, old_slug.slug if old_slug else None)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


