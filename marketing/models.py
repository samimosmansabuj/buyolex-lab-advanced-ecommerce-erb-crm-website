from django.db import models

class MarketingIntegration(models.Model):
    PROVIDER_CHOICES = [
        ('facebook_pixel', 'Facebook Pixel'),
        ('facebook_capi', 'Facebook Conversion API'),
        ('gtm', 'Google Tag Manager'),
        ('ga4', 'Google Analytics 4'),
    ]
    provider = models.CharField(max_length=64, choices=PROVIDER_CHOICES)
    config = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, default='inactive')
    last_tested_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} ({self.provider or 'global'})"


class MarketingEventLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    event_name = models.CharField(max_length=255)
    payload = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    response = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=64, default='pending')
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_name} for {self.event_name}"
