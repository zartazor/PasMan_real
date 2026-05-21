"""
Tests for the vault app
"""

from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import MasterPassword
from vault.models import Credential, AuditLog
from vault.encryption import encrypt_password, decrypt_password, derive_encryption_key
from vault.password_utils import PasswordGenerator, PasswordStrength


class EncryptionTestCase(TestCase):
    """Test encryption/decryption functionality"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.master_password = MasterPassword.objects.create(user=self.user)
        self.master_password.set_password('master-password-123')

    def test_encrypt_decrypt_password(self):
        """Test that passwords can be encrypted and decrypted"""
        plain_password = 'my-secret-password-123'
        master_pwd = 'master-password-123'
        
        # Derive key
        key = derive_encryption_key(master_pwd, self.master_password.salt)
        
        # Encrypt
        encrypted = encrypt_password(plain_password, key)
        self.assertNotEqual(encrypted, plain_password.encode())
        
        # Decrypt
        decrypted = decrypt_password(encrypted, key)
        self.assertEqual(decrypted, plain_password)

    def test_wrong_key_fails_decryption(self):
        """Test that wrong key cannot decrypt password"""
        plain_password = 'my-secret-password-123'
        master_pwd = 'master-password-123'
        wrong_pwd = 'wrong-password-123'
        
        # Derive keys
        correct_key = derive_encryption_key(master_pwd, self.master_password.salt)
        
        # Create second master password for wrong key
        wrong_user = User.objects.create_user(username='wronguser', password='pass')
        wrong_master_pwd = MasterPassword.objects.create(user=wrong_user)
        wrong_master_pwd.set_password(wrong_pwd)
        wrong_key = derive_encryption_key(wrong_pwd, wrong_master_pwd.salt)
        
        # Encrypt with correct key
        encrypted = encrypt_password(plain_password, correct_key)
        
        # Try to decrypt with wrong key
        decrypted = decrypt_password(encrypted, wrong_key)
        self.assertIsNone(decrypted)  # Should return None on failure


class PasswordGeneratorTestCase(TestCase):
    """Test password generation"""

    def test_generate_password_default(self):
        """Test default password generation"""
        password = PasswordGenerator.generate()
        self.assertEqual(len(password), 16)
        self.assertGreater(len(password), 0)

    def test_generate_password_custom_length(self):
        """Test custom password length"""
        password = PasswordGenerator.generate(length=32)
        self.assertEqual(len(password), 32)

    def test_generate_password_with_options(self):
        """Test password generation with specific options"""
        password = PasswordGenerator.generate(
            length=20,
            uppercase=True,
            lowercase=True,
            numbers=True,
            symbols=False
        )
        self.assertEqual(len(password), 20)
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))


class PasswordStrengthTestCase(TestCase):
    """Test password strength checking"""

    def test_weak_password(self):
        """Test weak password detection"""
        password = 'weak'
        score, label, color = PasswordStrength.score(password)
        self.assertEqual(score, 1)
        self.assertEqual(label, 'Weak')

    def test_strong_password(self):
        """Test strong password detection"""
        password = 'MyStr0ng!P@ssw0rd123'
        score, label, color = PasswordStrength.score(password)
        self.assertGreaterEqual(score, 4)

    def test_requirements_met(self):
        """Test password requirements checking"""
        password = 'MyP@ss123'
        requirements = PasswordStrength.get_requirements_met(password)
        
        self.assertTrue(requirements['lowercase'])
        self.assertTrue(requirements['uppercase'])
        self.assertTrue(requirements['numbers'])
        self.assertTrue(requirements['symbols'])


class CredentialModelTestCase(TestCase):
    """Test credential model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_credential(self):
        """Test creating a credential"""
        credential = Credential.objects.create(
            user=self.user,
            website_name='Gmail',
            website_url='https://gmail.com',
            username='user@gmail.com',
            encrypted_password=b'encrypted-data',
            category='email'
        )
        self.assertEqual(credential.website_name, 'Gmail')
        self.assertEqual(credential.username, 'user@gmail.com')

    def test_get_display_name(self):
        """Test credential display name"""
        credential = Credential.objects.create(
            user=self.user,
            website_name='Gmail',
            username='user@gmail.com',
            encrypted_password=b'encrypted-data'
        )
        self.assertEqual(credential.get_display_name(), 'Gmail (user@gmail.com)')


class AuditLogTestCase(TestCase):
    """Test audit logging"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.credential = Credential.objects.create(
            user=self.user,
            website_name='Gmail',
            username='user@gmail.com',
            encrypted_password=b'encrypted-data'
        )

    def test_create_audit_log(self):
        """Test creating an audit log"""
        log = AuditLog.objects.create(
            user=self.user,
            credential=self.credential,
            action='view',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.action, 'view')
        self.assertEqual(log.user, self.user)
