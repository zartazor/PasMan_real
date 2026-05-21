"""
Password utilities: generation, strength checking, etc.
"""

import secrets
import string
import re


class PasswordGenerator:
    """Generate secure random passwords"""

    @staticmethod
    def generate(length=16, uppercase=True, lowercase=True, numbers=True, symbols=True):
        """
        Generate a random password.
        
        Args:
            length: Password length (default 16)
            uppercase: Include uppercase letters
            lowercase: Include lowercase letters
            numbers: Include numbers
            symbols: Include symbols
        
        Returns:
            Generated password string
        """
        characters = ''
        if uppercase:
            characters += string.ascii_uppercase
        if lowercase:
            characters += string.ascii_lowercase
        if numbers:
            characters += string.digits
        if symbols:
            characters += string.punctuation

        if not characters:
            characters = string.ascii_letters + string.digits

        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password


class PasswordStrength:
    """Analyze password strength"""

    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4
    VERY_STRONG = 5

    @staticmethod
    def score(password):
        """
        Calculate password strength score (1-5).
        
        Args:
            password: Password to evaluate
        
        Returns:
            Tuple of (score, label, color)
        """
        score = 0
        length = len(password)

        # Length checks
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1

        # Complexity checks
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[0-9]', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1

        # Normalize to 1-5 scale
        final_score = min(max((score // 1), 1), 5)

        labels = {
            1: ("Weak", "red"),
            2: ("Fair", "orange"),
            3: ("Good", "yellow"),
            4: ("Strong", "green"),
            5: ("Very Strong", "darkgreen"),
        }

        label, color = labels.get(final_score, ("Unknown", "gray"))
        return final_score, label, color

    @staticmethod
    def get_requirements_met(password):
        """
        Return a dict of requirements met.
        """
        return {
            'length_8': len(password) >= 8,
            'length_12': len(password) >= 12,
            'length_16': len(password) >= 16,
            'lowercase': bool(re.search(r'[a-z]', password)),
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'numbers': bool(re.search(r'[0-9]', password)),
            'symbols': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
        }
