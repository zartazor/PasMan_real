# PasMan - Architecture & Design Guide

## 🏗️ System Architecture

### Overview
```
┌─────────────────────────────────────────────────────────────┐
│                     PASMAN ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  BROWSER                                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Frontend (HTML/CSS/JS)                              │    │
│  │ • User Registration & Login                         │    │
│  │ • Master Password Verification                      │    │
│  │ • Credential Display & Management                   │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │ HTTPS                              │
│  DJANGO SERVER                                               │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │ Views & Logic                                       │    │
│  │ • Authentication (accounts app)                     │    │
│  │ • Vault Operations (vault app)                      │    │
│  │ • Session Management                                │    │
│  └──────────┬───────────────────────────────┬──────────┘    │
│             │                               │                │
│  ┌──────────▼─────────────┐  ┌──────────────▼──────────┐    │
│  │ Models & Database      │  │ Security Layer          │    │
│  │ • User/Auth            │  │ • Encryption (Fernet)   │    │
│  │ • Credentials          │  │ • Key Derivation        │    │
│  │ • Audit Logs           │  │ (PBKDF2/Argon2)         │    │
│  └────────────┬───────────┘  └─────────────────────────┘    │
│               │                                               │
│  POSTGRESQL DATABASE                                          │
│  ┌───────────▼──────────────────────────────────────────┐   │
│  │ Encrypted Data Storage                               │   │
│  │ • Master passwords (Argon2 hashed)                   │   │
│  │ • Credentials (encrypted with Fernet)                │   │
│  │ • Audit trail (unencrypted for logging)              │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Security Flow

### User Registration → First Access
```
1. Register
   └─> Creates User (Django Auth)

2. Set Master Password
   └─> Argon2.hash(master_password)
   └─> Store hash in MasterPassword model
   └─> Generate salt for key derivation

3. Verify Master Password (Each Session)
   └─> Argon2.verify(input, stored_hash)
   └─> Derive PBKDF2 key
   └─> Store master_password in session cookie (encrypted)

4. Create Credential
   └─> user enters: website, username, password, etc.
   └─> Fernet.encrypt(password, derived_key)
   └─> Store encrypted bytes in DB

5. View Credential
   └─> Retrieve encrypted_password from DB
   └─> Get master_password from session
   └─> Fernet.decrypt(encrypted_password, derived_key)
   └─> Display decrypted password to user
```

### Key Derivation Process
```
Master Password (user input)
         ↓
PBKDF2(
  password=master_password,
  salt=stored_salt,
  algorithm=SHA256,
  iterations=100000,
  key_length=32
)
         ↓
Base64-encoded Fernet key
         ↓
Used for all credential encryption/decryption
```

## 🗂️ Code Organization

### `accounts/` - Authentication
```
accounts/
├── models.py
│   ├── MasterPassword      # Hash + salt storage
│   └── UserSession         # Session tracking
├── views.py
│   ├── register            # Create account
│   ├── login_view          # Django login
│   ├── setup_master_password
│   ├── verify_master_password
│   └── logout_view
├── forms.py                # Auth forms
└── admin.py                # Admin interface
```

### `vault/` - Password Manager
```
vault/
├── models.py
│   ├── Credential          # website, username, encrypted_password
│   └── AuditLog            # Access tracking
├── views.py
│   ├── dashboard           # List credentials
│   ├── credential_detail   # View + decrypt
│   ├── create_credential   # Add new
│   ├── edit_credential     # Update
│   ├── delete_credential   # Remove
│   ├── password_generator  # Generate strong passwords
│   └── API endpoints       # AJAX helpers
├── forms.py                # Credential forms
├── encryption.py           # Encrypt/decrypt utilities
├── password_utils.py       # Password generation & strength
└── admin.py                # Admin interface
```

### `templates/` - Frontend
```
templates/
├── base.html               # Layout + navigation
├── index.html              # Home page
├── accounts/
│   ├── login.html
│   ├── register.html
│   ├── setup_master_password.html
│   └── verify_master_password.html
└── vault/
    ├── dashboard.html
    ├── credential_detail.html
    ├── create_credential.html
    ├── edit_credential.html
    ├── password_generator.html
    └── confirm_delete.html
```

### `static/` - Frontend Assets
```
static/
├── css/
│   ├── pacman-theme.css    # Main styling + colors
│   └── animations.css      # Arcade animations
└── js/
    └── main.js             # Frontend utilities
```

## 🔄 Data Flow Examples

### Example 1: Creating a Credential
```
User submits form
    ↓
POST /vault/credential/create/
    ↓
create_credential view:
  ├─ Get master_password from session['master_password']
  ├─ Get MasterPassword.salt from DB
  ├─ Derive encryption key: PBKDF2(master_pw, salt)
  ├─ Encrypt password: Fernet.encrypt(password, key)
  └─ Save Credential with encrypted_password
    ↓
Database stores:
  {
    website_name: "Gmail",
    username: "user@gmail.com",
    encrypted_password: b'gAAAAABmDjx...'  (encrypted)
  }
```

### Example 2: Viewing a Credential
```
User clicks credential
    ↓
GET /vault/credential/123/
    ↓
credential_detail view:
  ├─ Get Credential from DB
  ├─ Get master_password from session['master_password']
  ├─ Get MasterPassword.salt from DB
  ├─ Derive decryption key: PBKDF2(master_pw, salt)
  ├─ Decrypt password: Fernet.decrypt(encrypted_password, key)
  ├─ Log access: AuditLog.create(action='view', ...)
  └─ Render template with decrypted_password
    ↓
Browser displays:
  Password: (hidden by default, show button to reveal)
```

## 🛡️ Security Guarantees

### What We Protect
- ✅ Master password never stored plaintext
- ✅ Credentials encrypted at rest (in database)
- ✅ HTTPS enforced in production
- ✅ Session-based access control
- ✅ All access logged for audit trail

### What We DON'T Protect
- ❌ Master password in-session (necessary for operation)
- ❌ Passwords in memory (decrypted in view)
- ❌ Browser storage (use secure cookies only)
- ❌ Client-side attacks (XSS, etc.) - use Content Security Policy

### Attack Vectors & Mitigations
| Attack | Mitigation |
|--------|-----------|
| Brute force master password | Rate limiting + Argon2 slow hashing |
| SQL injection | Django ORM parameterized queries |
| XSS | Template auto-escaping + CSP header |
| Session hijacking | Secure, HTTPOnly cookies + HTTPS |
| Man-in-the-middle | HTTPS enforcement in production |
| Password dictionary | Strong random generation + strength meter |

## 🔧 Extending PasMan

### Adding Two-Factor Authentication
```python
# In accounts/models.py
class TwoFactorSecret(models.Model):
    user = ForeignKey(User)
    secret = EncryptedField()  # TOTP secret
    backup_codes = JSONField()
    enabled = BooleanField(default=False)

# In accounts/views.py - Add after master password verification
def verify_totp(request):
    code = request.POST.get('totp_code')
    secret = TwoFactorSecret.objects.get(user=request.user)
    if pyotp.verify(secret.secret, code):
        # Mark session as fully authenticated
        request.session['totp_verified'] = True
```

### Adding Password Sharing
```python
# In vault/models.py
class SharedCredential(models.Model):
    credential = ForeignKey(Credential)
    shared_with = ForeignKey(User)
    access_level = CharField(choices=['view', 'edit'])
    expires_at = DateTimeField()

# Encrypt with shared user's public key
# Decrypt with their private key
```

### Adding CSV Export
```python
# In vault/views.py
def export_credentials_csv(request):
    credentials = Credential.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="credentials.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Website', 'Username', 'Email', 'Category'])
    
    for cred in credentials:
        # Decrypt passwords
        decrypted = decrypt_password(cred.encrypted_password, key)
        writer.writerow([cred.website_name, cred.username, cred.email, cred.category])
    
    return response
```

## 📊 Performance Considerations

### Database Queries
```python
# GOOD - Single query
credentials = Credential.objects.filter(user=request.user).values(
    'id', 'website_name', 'username'
)

# BAD - N+1 query problem
for cred in Credential.objects.all():
    print(cred.user.username)  # New query per credential!

# BETTER
credentials = Credential.objects.select_related('user')
for cred in credentials:
    print(cred.user.username)  # No extra queries
```

### Caching Strategy
```python
# Cache frequently accessed data
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
@login_required
def password_generator(request):
    # Password generation params don't change per user
    ...
```

## 🧪 Testing Strategy

### Unit Tests
- Encryption/decryption
- Password generation
- Password strength checking
- Model methods

### Integration Tests
- User registration flow
- Master password setup
- Credential CRUD operations
- Session management

### Security Tests
- Master password verification
- Wrong key decryption failure
- Audit logging accuracy
- CSRF protection

Run tests: `python manage.py test`

---

**Remember**: Security is an ongoing process, not a destination. Keep dependencies updated and monitor security advisories!
