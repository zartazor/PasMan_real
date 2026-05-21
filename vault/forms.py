"""
Forms for vault operations
"""

from django import forms
from vault.models import Credential
from vault.password_utils import PasswordStrength


class CredentialForm(forms.ModelForm):
    """
    Form for creating/editing credentials.
    """
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300',
            'placeholder': 'Enter password',
            'id': 'password-field'
        }),
        required=False,  # Can be empty for first save
    )

    class Meta:
        model = Credential
        fields = ['website_name', 'website_url', 'username', 'email', 'notes', 'category']
        widgets = {
            'website_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300',
                'placeholder': 'Website or service name'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300',
                'placeholder': 'https://example.com'
            }),
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300',
                'placeholder': 'Username or email'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300',
                'placeholder': 'Email address (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300',
                'placeholder': 'Additional notes...',
                'rows': 4
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300 focus:outline-none focus:border-yellow-300'
            }),
        }


class PasswordGeneratorForm(forms.Form):
    """
    Form for password generator settings
    """
    length = forms.IntegerField(
        label="Password Length",
        initial=16,
        min_value=8,
        max_value=128,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-purple-500 bg-gray-900 text-yellow-300'
        })
    )
    uppercase = forms.BooleanField(label="Uppercase Letters (A-Z)", required=False, initial=True)
    lowercase = forms.BooleanField(label="Lowercase Letters (a-z)", required=False, initial=True)
    numbers = forms.BooleanField(label="Numbers (0-9)", required=False, initial=True)
    symbols = forms.BooleanField(label="Symbols (!@#$...)", required=False, initial=True)


class SearchForm(forms.Form):
    """
    Form for searching credentials
    """
    query = forms.CharField(
        label="Search",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border-2 border-yellow-300 bg-gray-800 text-yellow-300 placeholder-gray-500 focus:outline-none focus:border-yellow-300 font-arcade',
            'placeholder': '🔍 Search your vault...'
        })
    )
    category = forms.ChoiceField(
        label="Category",
        required=False,
        choices=[('', 'All Categories')] + Credential._meta.get_field('category').choices,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 rounded-lg border-2 border-yellow-300 bg-gray-800 text-yellow-300 focus:outline-none focus:border-yellow-300'
        })
    )
