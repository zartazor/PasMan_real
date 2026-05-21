"""
Encryption utility functions for password management.
All passwords are encrypted using Fernet (symmetric encryption) with a key
derived from the user's master password.
"""
import os
from cryptography.fernet import Fernet, InvalidToken
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def derive_encryption_key(password: str, salt = None) -> bytes:
    """
    Derive a Fernet encryption key from a master password and salt.
    
    Args:
        password: Master password as string
        salt: Salt as bytes or hex string. If None, generates new salt.
    
    Returns:
        Base64-encoded Fernet key
    """
    # Handle salt input - could be hex string from database or bytes
    if salt is None:
        salt = os.urandom(16)
    elif isinstance(salt, str):
        # Convert hex string back to bytes
        salt = bytes.fromhex(salt)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,              # 256-bit key
        salt=salt,
        iterations=600_000,     # Good number for 2025+
    )
    key = kdf.derive(password.encode('utf-8'))
    # Return base64-encoded key for Fernet
    return base64.urlsafe_b64encode(key)


def encrypt_password(password, encryption_key):
    """
    Encrypt a password using Fernet.
    
    Args:
        password: Plain text password to encrypt
        encryption_key: Fernet key
    
    Returns:
        Encrypted password (bytes)
    """
    cipher = Fernet(encryption_key)
    encrypted = cipher.encrypt(password.encode())
    return encrypted


def decrypt_password(encrypted_password, encryption_key):
    """
    Decrypt a password using Fernet.
    
    Args:
        encrypted_password: Encrypted password (bytes)
        encryption_key: Fernet key
    
    Returns:
        Plain text password or None if decryption fails
    """
    try:
        cipher = Fernet(encryption_key)
        decrypted = cipher.decrypt(encrypted_password)
        return decrypted.decode()
    except (InvalidToken, Exception):
        return None
