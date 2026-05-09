from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Store", {"fields": ("is_vendor", "phone", "email_verified")}),
    )
    list_display = ("username", "email", "email_verified", "is_vendor", "is_staff", "is_superuser")
