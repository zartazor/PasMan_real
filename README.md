# 🎮 PasMan - Arcade Password Manager (Fun Project)

> A retro Pac-Man themed password manager built with Django + PostgreSQL

![PasMan](https://img.shields.io/badge/version-1.0.0-yellow) ![License](https://img.shields.io/badge/license-MIT-blue) ![Security](https://img.shields.io/badge/encryption-AES--256-green)

## 🟡 Features

### 🔐 Security First
- **Master Password**: Single strong password to access your vault
- **AES-256 Encryption**: All passwords encrypted with military-grade encryption (Fernet)
- **Zero-Knowledge Architecture**: Server never sees plaintext passwords
- **Argon2 Hashing**: Master password securely hashed with Argon2
- **Audit Logging**: Track all vault access and actions

### 🎲 Password Management
- **CRUD Operations**: Create, read, update, delete credentials
- **Password Generator**: Generate strong random passwords with custom settings
- **Password Strength Meter**: Real-time password strength analysis (1-5 scale)
- **Search & Filter**: Find credentials by website, username, or category
- **Clipboard Copy**: Safely copy usernames/passwords with audit logging

### 🎨 User Experience
- **Retro Pac-Man Theme**: Neon yellow (#FFEE00), pink (#FF00FF), blue gradients
- **Arcade Aesthetic**: Pixel fonts, maze-inspired elements, glowing borders
- **Responsive Design**: Works on desktop, tablet, mobile
- **Dark Mode Only**: Eye-friendly dark interface with neon accents
- **No Tracking**: Privacy-focused, no analytics

### 📊 Vault Features
- **Categories**: Email, Social Media, Work, Finance, Other
- **Website Links**: Direct links to services
- **Notes**: Store additional information about each credential
- **Metadata**: Track creation and last-modified dates
- **Bulk Management**: Search, filter, and organize credentials

## 📋 Tech Stack

```
Backend:     Django 5.1
Database:    PostgreSQL (or SQLite for dev)
Frontend:    HTML5 + Tailwind CSS + Vanilla JavaScript
Encryption:  cryptography (Fernet) + Argon2
Auth:        Django Auth + Master Password
Deployment:  Render.com (Web) + Supabase (DB)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip & virtualenv
- PostgreSQL (optional for production)

### Local Development

1. **Clone and setup virtual environment**
   ```bash
   cd PasMan_real
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**
   ```
   SECRET_KEY=your-secret-key-here-change-in-production
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

4. **Initialize database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional: admin access
   ```

5. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

   Visit: http://localhost:8000

### First Time Setup

1. **Register a new account** at `/accounts/register/`
2. **Login** with your credentials
3. **Set Master Password** - This protects your entire vault
4. **Verify Master Password** each session to unlock the vault
5. **Start adding credentials!**

## 📁 Project Structure

```
PasMan_real/
├── pasman/                 # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI entry point
├── accounts/              # Authentication app
│   ├── models.py          # MasterPassword, UserSession
│   ├── views.py           # Login, register, master password
│   ├── forms.py           # Auth forms
│   └── urls.py            # Auth routes
├── vault/                 # Password manager app
│   ├── models.py          # Credential, AuditLog
│   ├── views.py           # Vault operations
│   ├── forms.py           # Credential forms
│   ├── encryption.py      # Encryption utilities
│   ├── password_utils.py  # Password generation & strength
│   └── urls.py            # Vault routes
├── templates/             # HTML templates
│   ├── base.html          # Base layout
│   ├── index.html         # Home page
│   ├── accounts/          # Auth templates
│   └── vault/             # Vault templates
├── static/                # CSS, JavaScript
│   ├── css/
│   │   ├── pacman-theme.css    # Main theme
│   │   └── animations.css      # Arcade animations
│   └── js/
│       └── main.js        # Frontend JavaScript
├── manage.py              # Django CLI
└── requirements.txt       # Python dependencies
```

## 🔐 Security Architecture

### Master Password Flow
```
User Input → Argon2 Hash → Stored in DB
         ↓
User Verification → Compare Hash
         ↓
Derive PBKDF2 Key → Session Storage
         ↓
Use for Credential Encryption/Decryption
```

### Credential Encryption
```
Plain Password → Fernet Cipher (with derived key) → Encrypted bytes → DB storage
Encrypted bytes → Fernet Decipher (with derived key) → Plain Password → Display
```

### Zero-Knowledge Guarantee
- Master password never sent to server (used locally only)
- Credentials only encrypted/decrypted client-side in the vault view
- Server stores only encrypted blobs
- Even database admins can't see passwords

## 🎨 Arcade Theme Colors

| Element | Color | Hex |
|---------|-------|-----|
| Primary (Pac-Man) | Yellow | `#FFEE00` |
| Secondary (Pink Ghost) | Magenta | `#FF00FF` |
| Tertiary (Blue Ghost) | Blue | `#0088FF` |
| Background | Dark Navy | `#0a0e27` |
| Dark Accent | Darker Navy | `#050811` |
| Border | Bright Yellow | `#FFEE00` |

### Fonts
- **Arcade**: Press Start 2P (Google Fonts)
- **Code**: Monospace for passwords

## 🛠️ API Endpoints

### Authentication
- `GET/POST /accounts/login/` - User login
- `GET/POST /accounts/register/` - New account registration
- `GET/POST /accounts/setup-master-password/` - Initial master password setup
- `GET/POST /accounts/verify-master-password/` - Unlock vault
- `GET /accounts/logout/` - Logout and clear session

### Vault
- `GET /vault/` - Dashboard (list all credentials)
- `GET /vault/credential/<id>/` - View credential details
- `GET/POST /vault/credential/create/` - Create new credential
- `GET/POST /vault/credential/<id>/edit/` - Edit credential
- `GET/POST /vault/credential/<id>/delete/` - Delete credential
- `GET /vault/password-generator/` - Password generator
- `POST /vault/api/copy-log/<id>/` - Log copy action
- `GET /vault/api/password-check/` - Check password strength (AJAX)

## 🔐 Master Password Requirements

- Minimum 8 characters
- Recommended: 12+ characters
- Should include: uppercase, lowercase, numbers, symbols
- Never share or write down
- **If lost, your vault is unrecoverable**

## ⚙️ Configuration

### Environment Variables (`.env`)
```
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False  # Set to False in production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### Database Configuration

**Development (SQLite)**
```python
# Auto-configured in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Production (PostgreSQL)**
```python
# Uncomment in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

## 🧪 Testing

### Test User Creation
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin123456!
```

### Manual Testing Checklist
- [ ] Register new account
- [ ] Set master password
- [ ] Login and verify master password
- [ ] Create credential with password generator
- [ ] View and copy password
- [ ] Edit credential
- [ ] Search/filter credentials
- [ ] Delete credential
- [ ] Generate strong passwords
- [ ] Check password strength meter
- [ ] Logout clears session

## 🚨 Important Security Notes

1. **Master Password is Everything**
   - If lost, vault is permanently inaccessible
   - Make it memorable but strong
   - Don't store it anywhere

2. **HTTPS in Production**
   - Always use HTTPS
   - Settings auto-enable in `DEBUG=False`
   - Use Let's Encrypt for free SSL

3. **Database Backups**
   - Encrypted data is safe to backup
   - Only plaintext master passwords (which aren't stored) need protection

4. **Session Security**
   - Session cookie is secure and HTTPOnly
   - Master password verified once per session
   - Session timeout recommended after inactivity

5. **Audit Logging**
   - All access is logged
   - Check audit logs regularly for suspicious activity

## 🐛 Troubleshooting

### "Incorrect master password"
- Check CAPS LOCK
- Verify you're using the correct master password
- If forgotten, only option is account deletion and new registration

### Credentials not loading
- Clear browser cache
- Refresh page
- Check browser console for errors

### Encryption errors
- Verify `PBKDF2` key derivation is working
- Check for database corruption
- Ensure `cryptography` library is installed

### Database connection issues
- PostgreSQL service running?
- Check `DATABASE_URL` in `.env`
- Verify credentials and host are correct

## 📱 Browser Support

| Browser | Support |
|---------|---------|
| Chrome/Chromium | ✅ Full |
| Firefox | ✅ Full |
| Safari | ✅ Full |
| Edge | ✅ Full |
| IE 11 | ❌ Not supported |

## 🚀 Future Enhancements

- [ ] Two-Factor Authentication (2FA)
- [ ] Password strength history
- [ ] Credential sharing (encrypted)
- [ ] Browser extension auto-fill
- [ ] CSV/JSON import/export
- [ ] Password breach checking (HaveIBeenPwned API)
- [ ] Passkey/WebAuthn support
- [ ] Mobile app (React Native)
- [ ] End-to-end sharing
- [ ] Offline mode

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This is a demonstration project. For production use:
- Conduct security audit
- Use professional penetration testing
- Implement rate limiting
- Add CAPTCHA
- Use secure hosting
- Enable monitoring

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Review security documentation
- Check deployment guide

---

**Built with ❤️ by Luke**  
🎮 *Keep your secrets safe in the arcade* 🎮
