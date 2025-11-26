from django.db import models

class LandingPageHeroType(models.TextChoices):
    IMAGE = "image"
    VIDEO = "video"
