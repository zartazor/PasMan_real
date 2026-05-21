"""
Tests for the accounts app
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import MasterPassword


class MasterPasswordTestCase(TestCase):
    """Test master password functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.master_password = MasterPassword.objects.create(user=self.user)

    def test_set_and_verify_password(self):
        """Test setting and verifying master password"""
        password = 'my-super-secure-master-password'
        self.master_password.set_password(password)
        
        # Verify it was hashed
        self.assertNotEqual(self.master_password.password_hash, password)
        
        # Verify correct password works
        self.assertTrue(self.master_password.verify_password(password))
        
        # Verify wrong password fails
        self.assertFalse(self.master_password.verify_password('wrong-password'))

    def test_encryption_key_derivation(self):
        """Test that encryption key can be derived"""
        password = 'test-master-password'
        self.master_password.set_password(password)
        
        # Should not raise exception
        key = self.master_password.get_encryption_key(password)
        self.assertIsNotNone(key)


class AuthenticationTestCase(TestCase):
    """Test authentication flows"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_register_view(self):
        """Test user registration"""
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'password': 'newpass123456',
            'password_confirm': 'newpass123456'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_login_view(self):
        """Test user login"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
