from django.db import models

class EmailConfigMailType(models.TextChoices):
    INFO  = "info"
    NO_REPLY  = "no_reply"
    CONTACT  = "contact"
    CAREER  = "career"

class EmailConfigServerType(models.TextChoices):
    SMTP = "smtp"
    API = "api"

