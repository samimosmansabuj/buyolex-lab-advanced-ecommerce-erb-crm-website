from django.db import models

class MarketingIntegrationProviderChoices(models.TextChoices):
    facebook_pixel = "facebook_pixel"
    facebook_capi = "facebook_capi"
    gtm = "gtm"
    ga4 = "ga4"

class MarketingIntegrationStatusChoices(models.TextChoices):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class EmailConfigMailType(models.TextChoices):
    INFO  = "info"
    NO_REPLY  = "no_reply"
    CONTACT  = "contact"
    CAREER  = "career"

class EmailConfigServerType(models.TextChoices):
    SMTP = "smtp"
    API = "api"

