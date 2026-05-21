# 🚀 PasMan Deployment Guide

Deploy PasMan to production using Render.com (web) + Supabase (database)

## 📋 Prerequisites

1. **GitHub Account** - For code hosting
2. **Render Account** - For hosting (https://render.com)
3. **Supabase Account** - For PostgreSQL database (https://supabase.com)
4. **Git** - Version control

---

## Step 1: Prepare Your Repository

### 1.1 Initialize Git Repository (if not already done)
```bash
cd PasMan_real
git init
git add .
git commit -m "Initial commit: PasMan password manager"
```

### 1.2 Create `.gitignore`
```bash
cat > .gitignore << 'EOF'
# Environment
.env
.env.local
venv/
env/

# Database
*.sqlite3
db.sqlite3

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Media & Static
/media/
/staticfiles/
*.log

# OS
.DS_Store
Thumbs.db
EOF
git add .gitignore
git commit -m "Add .gitignore"
```

### 1.3 Create Production Settings Module
```bash
cat > pasman/settings_production.py << 'EOF'
from .settings import *
import os

# Production-specific settings
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database - PostgreSQL from Supabase
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

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'style-src': ("'self'", "'unsafe-inline'", "fonts.googleapis.com"),
    'script-src': ("'self'", "cdn.tailwindcss.com"),
    'font-src': ("'self'", "fonts.gstatic.com"),
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
EOF
```

### 1.4 Update `requirements.txt` for Production
```bash
cat > requirements.txt << 'EOF'
Django==5.1.1
psycopg2-binary==2.9.9
python-decouple==3.8
cryptography==41.0.7
Pillow==10.1.0
argon2-cffi==23.1.0
django-crispy-forms==2.1
crispy-tailwind==0.5.1
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
EOF
```

### 1.5 Create `Procfile` for Render
```bash
cat > Procfile << 'EOF'
web: gunicorn pasman.wsgi:application --log-file -
release: python manage.py migrate
EOF
```

### 1.6 Create `runtime.txt` for Python Version
```bash
echo "python-3.11.6" > runtime.txt
```

### 1.7 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/PasMan.git
git branch -M main
git push -u origin main
```

---

## Step 2: Set Up Supabase Database

### 2.1 Create Supabase Project
1. Go to https://supabase.com
2. Sign in or create account
3. Click "New Project"
4. Fill in project details:
   - Name: `pasman`
   - Database Password: Create strong password
   - Region: Choose closest to you
5. Click "Create new project"

### 2.2 Get Database Credentials
1. Go to Project Settings → Database
2. Copy connection string (PostgreSQL)
3. Note the following:
   - **Host**: `db.xxxxx.supabase.co`
   - **Port**: `5432`
   - **Database**: `postgres`
   - **User**: `postgres`
   - **Password**: Your chosen password

### 2.3 Create Connection Pool (Optional but Recommended)
1. In Supabase: Settings → Database → Connection Pooling
2. Enable connection pooling
3. Session mode: Use for connections
4. Copy pool connection string

---

## Step 3: Deploy to Render

### 3.1 Create Render Account
1. Go to https://render.com
2. Sign in with GitHub
3. Connect your GitHub account

### 3.2 Create New Web Service
1. Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Search for `PasMan_real` and select it

### 3.3 Configure Render Service
1. **Name**: `pasman`
2. **Environment**: `Python 3`
3. **Build Command**: 
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```
4. **Start Command**:
   ```
   gunicorn pasman.wsgi:application
   ```
5. **Instance Type**: Free (or Starter for better performance)

### 3.4 Add Environment Variables
1. In Render dashboard → Environment tab
2. Add each variable:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourdomain.onrender.com` |
| `DJANGO_SETTINGS_MODULE` | `pasman.settings_production` |
| `DB_NAME` | `postgres` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | Your Supabase password |
| `DB_HOST` | Supabase host (e.g., `db.xxxxx.supabase.co`) |
| `DB_PORT` | `5432` |

### 3.5 Deploy
1. Click "Deploy"
2. Render will automatically:
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start gunicorn server

Monitor deployment in "Logs" tab.

---

## Step 4: Run Database Migrations

### 4.1 Access Render Shell (if needed)
```bash
# Render provides logs, but for CLI access:
# 1. Go to Render dashboard
# 2. Select service → Shell tab
# 3. Run migrations there

python manage.py migrate
python manage.py createsuperuser  # Optional
```

### 4.2 Verify Deployment
1. Visit your Render URL: `https://pasman.onrender.com`
2. You should see the PasMan home page
3. Register a new account
4. Test full workflow

---

## Step 5: Set Up Custom Domain (Optional)

### 5.1 Add Custom Domain in Render
1. Render Dashboard → Service Settings
2. "Custom Domains" section
3. Add your domain (e.g., `pasman.yourdomain.com`)
4. Copy CNAME record

### 5.2 Update DNS Records
1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Add CNAME record pointing to Render
3. DNS changes may take 24-48 hours

---

## Step 6: Enable HTTPS

### 6.1 Automatic with Render
- Render automatically provisions SSL/TLS with Let's Encrypt
- HTTPS is enabled by default
- Verify: Check URL bar for 🔒 lock icon

---

## Step 7: Monitor & Maintain

### 7.1 Set Up Monitoring
1. Render Dashboard → Alerts
2. Enable email notifications for:
   - Deploy failures
   - Instance restarts
   - Memory usage

### 7.2 View Logs
1. Render Dashboard → Logs tab
2. Monitor for errors
3. Check weekly

### 7.3 Database Backups
1. Supabase Dashboard → Backups
2. Automatic daily backups enabled
3. Download backups if needed

### 7.4 Updates
1. Make changes locally
2. Push to GitHub: `git push origin main`
3. Render auto-deploys on new commits

---

## 🚨 Production Security Checklist

- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is strong and random
- [ ] HTTPS enforced (automatic with Render)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] PostgreSQL password is strong
- [ ] Database credentials in environment variables (not in code)
- [ ] Regular backups configured
- [ ] Monitor logs for errors
- [ ] Rate limiting considered
- [ ] Admin interface secured (change default URLs)

---

## 🔧 Troubleshooting

### Deployment Fails
1. Check Render logs for error messages
2. Verify all environment variables are set
3. Ensure `requirements.txt` has all dependencies
4. Check `Procfile` syntax

### Database Connection Error
```
psycopg2.OperationalError: could not connect to server
```
**Solution**:
- Verify Supabase credentials in environment variables
- Check firewall: Supabase → Settings → Network → IP Whitelist
- Ensure database is running

### Static Files Not Loading
```
Render logs show 404 on CSS/JS
```
**Solution**:
- Ensure `collectstatic` runs in build command
- Check `STATIC_ROOT` and `STATIC_URL` in settings
- Verify WhiteNoise is installed

### Import Errors
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution**:
- Add module to `requirements.txt`
- Rebuild service in Render: Deploy → Redeploy latest commit

### Slow Performance
- Upgrade Render instance type
- Enable caching in browser
- Optimize database queries
- Consider CDN for static files

---

## 📊 Scaling for Production

### Current Capacity (Free Tier)
- ~100 concurrent users
- 512MB RAM
- Basic PostgreSQL

### Upgrade Options
1. **Render Starter Plan**: $7/month
   - Better performance
   - 30GB storage

2. **Supabase Pro Plan**: $25/month
   - 500GB storage
   - Better API limits

3. **Load Balancing**: For 1000+ users
   - Multiple Render services
   - Database connection pooling

---

## 🔄 CI/CD Pipeline (Optional)

### Automatic Testing Before Deploy
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test
```

---

## 📧 Email Configuration (Optional)

For password reset emails, add to environment variables:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🆘 Getting Help

- **Render Support**: https://render.com/help
- **Supabase Docs**: https://supabase.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **GitHub Issues**: Check repository issues

---

## ✅ Deployment Completed!

Your PasMan password manager is now live! 🎉

### Next Steps
1. Create admin account
2. Configure security settings
3. Set up monitoring
4. Share with users
5. Monitor performance

### Key URLs
- **App**: https://yourdomain.onrender.com
- **Admin**: https://yourdomain.onrender.com/admin
- **Database**: Supabase console

---

**Remember**: Keep your `SECRET_KEY` and database password safe!
