from .models import MarketingIntegration
from .utix import MarketingIntegrationStatusChoices, MarketingIntegrationProviderChoices

def marketing_setup_credentials(request):
    facebook_pixel = MarketingIntegration.objects.filter(
        provider=MarketingIntegrationProviderChoices.facebook_pixel, status=MarketingIntegrationStatusChoices.ACTIVE
    ).first()
    return {
        'FACEBOOK_PIXEL_ID': facebook_pixel.config["pixel_id"] if facebook_pixel and facebook_pixel.config else None
    }
