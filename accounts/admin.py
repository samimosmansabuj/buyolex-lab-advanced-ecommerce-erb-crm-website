from django.contrib import admin
from .models import *


admin.site.register(Role)
admin.site.register(RolePermission)
admin.site.register(CustomUser)
