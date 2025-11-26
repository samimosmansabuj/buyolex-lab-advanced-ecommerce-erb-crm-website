from django.shortcuts import render
from .models import HomePageLandingPage
from catalog.utix import PRODUCT_MEDIA_ROLE
from .utix import LandingPageHeroType
from settings_app.models import WhyBuyolex, DeliveryReturnPolicy

def product_landing_page(request):
    whybuyolex = WhyBuyolex.objects.first()
    deliveryreturnpolicy = DeliveryReturnPolicy.objects.first()
    landing_page_product = HomePageLandingPage.objects.filter(is_active=True).first()
    product = landing_page_product.product
    if len(product.videos.all()) > 0 and landing_page_product.hero_type == LandingPageHeroType.VIDEO:
        primary_hero = product.videos.all().first()
    else:
        primary_hero = product.images.filter(role=PRODUCT_MEDIA_ROLE.PRIMARY).first()
    
    return render(request, "product_landing_page.html", {"landing_page_product": landing_page_product, "primary_hero": primary_hero, "whybuyolex": whybuyolex, "deliveryreturnpolicy": deliveryreturnpolicy})

