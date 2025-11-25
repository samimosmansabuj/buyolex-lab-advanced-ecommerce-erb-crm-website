from django.db import models
from django.contrib.auth.models import AbstractUser
from .utix import USER_TYPE
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid

class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class RolePermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module_name = models.CharField(max_length=128)
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module_name')

    def __str__(self) -> str:
        return self.module_name

class CustomUser(AbstractUser):
    uuid = models.CharField(max_length=100, editable=False, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=14, blank=True, null=True)
    full_name = models.CharField(max_length=50, blank=True)
    profile_photo = models.ImageField(upload_to="user/profile_picture/", blank=True, null=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE.choices, default=USER_TYPE.CUSTOMER)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    joined_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def update_staff_superuser(self):
        if self.user_type == USER_TYPE.ADMIN:
            self.is_staff = True
            self.is_superuser = False
        elif self.user_type == USER_TYPE.SUPER_ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.user_type == USER_TYPE.STAFF:
            self.is_staff = True
            self.is_superuser = False
    
    def save(self, *args, **kwargs):
        self.update_staff_superuser()
        super().save(*args, **kwargs)






