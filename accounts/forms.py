"""
Forms for authentication
"""

from django import forms
from django.contrib.auth.models import User
from accounts.models import MasterPassword


class MasterPasswordForm(forms.Form):
    """
    Form for setting/verifying the master password.
    """
    password = forms.CharField(
        label="Master Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300 font-arcade',
            'placeholder': 'Enter your master password'
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError("Master password must be at least 8 characters long.")
        return password


class MasterPasswordVerifyForm(forms.Form):
    """
    Form for verifying the master password on login.
    """
    password = forms.CharField(
        label="Master Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300 font-arcade',
            'placeholder': 'Enter your master password'
        })
    )
