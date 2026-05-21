# PasMan Local Development Setup Guide

## Quick Start

### 1. Setup Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create .env File
```bash
# Copy the example
cp .env.example .env

# Edit with your settings
nano .env  # or use your editor
```

### 4. Initialize Database
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: something-strong!
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## Development Commands

### Create Test Data
```bash
python manage.py shell

# Inside Django shell:
from django.contrib.auth.models import User
from accounts.models import MasterPassword
from vault.models import Credential

# Create test user
user = User.objects.create_user(username='testuser', password='testpass123')

# Create master password
mp = MasterPassword.objects.create(user=user)
mp.set_password('my-master-password-123')

# List all users
User.objects.all().values('username', 'email')

# Exit
exit()
```

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test accounts
python manage.py test vault

# With verbosity
python manage.py test -v 2
```

### Database Operations
```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show SQL for migration
python manage.py sqlmigrate app_name migration_number

# Reset database
python manage.py flush
```

### Django Shell
```bash
python manage.py shell

# Example queries:
from django.contrib.auth.models import User
users = User.objects.all()
for user in users:
    print(user.username)

from vault.models import Credential
creds = Credential.objects.filter(user=user)
```

### Superuser Login
1. Visit: http://localhost:8000/admin/
2. Login with superuser credentials
3. Manage users, credentials, audit logs

---

## Troubleshooting

### Virtual Environment Issues
```bash
# If venv doesn't activate
python -m venv venv --clear

# Reinstall packages
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Errors
```bash
# Reset database (loses all data)
python manage.py flush

# Delete migrations except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
# Clear and recollect static files
rm -rf staticfiles/
python manage.py collectstatic --noinput
```

### Port Already in Use
```bash
# Run on different port
python manage.py runserver 8001

# Or kill the process using 8000
# On Windows: netstat -ano | findstr :8000
# On macOS/Linux: lsof -i :8000 | grep LISTEN
```

---

## File Structure

```
PasMan_real/
├── pasman/                 # Project config
│   ├── __init__.py
│   ├── settings.py        # Main settings
│   ├── settings_production.py  # Production config
│   ├── urls.py            # URL routing
│   ├── asgi.py            # ASGI config
│   └── wsgi.py            # WSGI config
├── accounts/              # Authentication
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py           # Django admin
│   ├── apps.py            # App config
│   ├── forms.py           # Forms
│   ├── models.py          # Models
│   ├── tests.py           # Tests
│   ├── urls.py            # URL routing
│   └── views.py           # Views
├── vault/                 # Main app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py           # Django admin
│   ├── apps.py            # App config
│   ├── encryption.py      # Encryption
│   ├── forms.py           # Forms
│   ├── models.py          # Models
│   ├── password_utils.py  # Utilities
│   ├── tests.py           # Tests
│   ├── urls.py            # URL routing
│   └── views.py           # Views
├── templates/             # HTML
│   ├── base.html
│   ├── index.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── setup_master_password.html
│   │   └── verify_master_password.html
│   └── vault/
│       ├── dashboard.html
│       ├── credential_detail.html
│       ├── create_credential.html
│       ├── edit_credential.html
│       ├── password_generator.html
│       └── confirm_delete.html
├── static/                # CSS, JS
│   ├── css/
│   │   ├── pacman-theme.css
│   │   └── animations.css
│   └── js/
│       └── main.js
├── media/                 # User uploads
├── staticfiles/           # Collected static (production)
├── .env.example           # Environment template
├── .gitignore
├── manage.py              # Django CLI
├── requirements.txt       # Dependencies
├── Procfile               # Deployment config
├── README.md              # Documentation
└── DEPLOYMENT.md          # Deployment guide
```

---

## Tips for Development

### Use Django Debug Toolbar
```bash
pip install django-debug-toolbar
```

Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]
```

### Code Style
- Use black for formatting: `pip install black && black .`
- Use flake8 for linting: `pip install flake8 && flake8 .`
- Follow PEP 8 style guide

### Performance Tips
1. Use `select_related()` for foreign keys
2. Use `prefetch_related()` for reverse relations
3. Index frequently queried fields
4. Cache expensive operations

### Security in Development
- Never commit `.env` file
- Use strong test passwords
- Don't use production data in development
- Keep dependencies updated

---

## Useful Links

- Django Docs: https://docs.djangoproject.com
- cryptography: https://cryptography.io
- Tailwind CSS: https://tailwindcss.com
- Supabase: https://supabase.com
- Render: https://render.com

---

Happy developing! 🚀
