"""
Models for user authentication and master password management.
"""

from django.db import models
from django.contrib.auth.models import User
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash
import os
from cryptography.fernet import Fernet


class MasterPassword(models.Model):
    """
    Stores the hashed master password for a user.
    The master password is never stored in plain text.
    It's hashed using Argon2 for storage.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_password')
    password_hash = models.CharField(max_length=255)  # Argon2 hash
    salt = models.CharField(max_length=255)  # Salt used for key derivation
    created_at = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Master Password"
        verbose_name_plural = "Master Passwords"

    def __str__(self):
        return f"Master Password for {self.user.username}"

    def set_password(self, password):
        """
        Hash and store the master password using Argon2.
        Also generates and stores a salt for encryption key derivation.
        """
        hasher = PasswordHasher()
        self.password_hash = hasher.hash(password)
        self.salt = os.urandom(16).hex()
        self.save()

    def verify_password(self, password):
        """
        Verify that the provided password matches the stored hash.
        Returns True if valid, False otherwise.
        """
        hasher = PasswordHasher()
        try:
            hasher.verify(self.password_hash, password)
            return True
        except (InvalidHash, Exception):
            return False

    def get_encryption_key(self, password):
        """
        Derive an encryption key from the master password and salt.
        This key is used to encrypt/decrypt stored passwords.
        Returns a Fernet key.
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        from cryptography.hazmat.backends import default_backend
        import base64

        # PBKDF2 key derivation
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes.fromhex(self.salt),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key


class UserSession(models.Model):
    """
    Tracks user session data including master password verification.
    This ensures the master password is verified before accessing the vault.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='session')
    is_authenticated = models.BooleanField(default=False)
    last_verified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.user.username}"
