from django.db import models

class ATTRIBUTE_TYPE(models.TextChoices):
    TEXT = "text"
    NUMBER = "number"
    DROPDOWN = "dropdown"
    COLOR = "color"
    SWATCH = "swatch"

class CATEGORY_STATUS(models.TextChoices):
    ACTIVE = "active"
    DEACTIVE = "deactive"
    DELETE = "delete"
    DRAFT = "draft"




class PRODUCT_TYPE(models.TextChoices):
    SIMPLE = "simple"
    VARIABLE = "variable"
    DIGITAL = "digital"
    SERVICE = "service"

class PRODUCT_STATUS(models.TextChoices):
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
    DELETE = "delete"
    DRAFT = "draft"

class PRODUCT_MEDIA_TYPE(models.TextChoices):
    IMAGE = "image"
    VIDEO = "video"

class PRODUCT_MEDIA_ROLE(models.TextChoices):
    PRIMARY = "primary"
    GALLERY = "gallery"
    ATTRIBUTE = "attribute"
    HERO = "hero"


