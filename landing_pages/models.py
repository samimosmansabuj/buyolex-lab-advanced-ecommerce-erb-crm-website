from django.db import models
from catalog.models import Product
from .utix import LandingPageHeroType


class HomePageLandingPage(models.Model):
    product = models.OneToOneField(Product, on_delete=models.SET_NULL, blank=True, null=True)
    product_details_section_title = models.CharField(max_length=255, blank=True, null=True)
    product_variation_section_title = models.CharField(max_length=255, blank=True, null=True)
    why_buyolex_section_title = models.CharField(max_length=255, blank=True, null=True)
    review_section_title = models.CharField(max_length=255, blank=True, null=True)
    policy_section_title = models.CharField(max_length=255, blank=True, null=True)
    hero_type = models.CharField(max_length=20, choices=LandingPageHeroType.choices, default=LandingPageHeroType.IMAGE)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Landing Page for Home - {self.product.title if self.product else "No Product"}"
