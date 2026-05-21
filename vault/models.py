"""
Models for the password vault.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Credential(models.Model):
    """
    A stored credential (username/password for a website or service).
    Passwords are stored encrypted.
    """
    # User ownership
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')

    # Credential information
    website_name = models.CharField(max_length=255, help_text="Name of the service (e.g., Gmail)")
    website_url = models.URLField(blank=True, null=True, help_text="URL of the service")
    username = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)

    # Encrypted password (stored as bytes)
    encrypted_password = models.BinaryField()

    # Additional info
    notes = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=50,
        default='other',
        choices=[
            ('email', 'Email'),
            ('social', 'Social Media'),
            ('work', 'Work'),
            ('finance', 'Finance'),
            ('other', 'Other'),
        ]
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Credential"
        verbose_name_plural = "Credentials"

    def __str__(self):
        return f"{self.username} @ {self.website_name}"

    def get_display_name(self):
        """Return a safe display name for the credential."""
        return f"{self.website_name} ({self.username})"


class AuditLog(models.Model):
    """
    Audit trail for credential access/modifications.
    For security tracking.
    """
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('view', 'Viewed'),
        ('edit', 'Edited'),
        ('delete', 'Deleted'),
        ('copy_password', 'Password Copied'),
        ('copy_username', 'Username Copied'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    credential = models.ForeignKey(
        Credential,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        credential_str = self.credential.get_display_name() if self.credential else "Unknown"
        return f"{self.user.username} - {self.action} - {credential_str}"
