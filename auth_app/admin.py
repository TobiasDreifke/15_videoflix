from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets