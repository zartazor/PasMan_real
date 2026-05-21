"""
Admin configuration for vault app
"""

from django.contrib import admin
from .models import Credential, AuditLog


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ('website_name', 'username', 'user', 'category', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('website_name', 'username', 'email')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Credential Info', {'fields': ('website_name', 'website_url', 'username', 'email')}),
        ('Security', {'fields': ('encrypted_password', 'category')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def has_add_permission(self, request):
        # Add through the web interface, not admin
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'credential', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'credential', 'action', 'timestamp', 'ip_address')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
