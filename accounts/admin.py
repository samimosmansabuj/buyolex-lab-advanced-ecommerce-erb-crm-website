from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin




admin.site.register(Role)
admin.site.register(RolePermission)
admin.site.register(CustomUser)
admin.site.register(CustomerAddress)

@admin.register(CustomerProfile)
class CustomCustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user__email", "phone", "full_name", "profile_uuid"]
    readonly_fields = ["profile_uuid"]

