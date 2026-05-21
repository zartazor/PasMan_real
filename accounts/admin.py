"""
Admin configuration for accounts app
"""

from django.contrib import admin
from .models import MasterPassword, UserSession


@admin.register(MasterPassword)
class MasterPasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'last_changed')
    readonly_fields = ('created_at', 'last_changed')
    fields = ('user', 'created_at', 'last_changed')

    def has_add_permission(self, request):
        return False


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_authenticated', 'last_verified')
    readonly_fields = ('last_verified',)
