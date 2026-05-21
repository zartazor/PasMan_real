"""
Views for user authentication and master password management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from accounts.models import MasterPassword, UserSession
from accounts.forms import MasterPasswordForm, MasterPasswordVerifyForm


def setup_master_password(request):
    """
    Initial setup: User sets their master password after account creation.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # Check if master password already exists
    try:
        master_pwd = MasterPassword.objects.get(user=request.user)
        # If exists, mark session as verified and go to dashboard
        request.session['master_password_verified'] = True
        return redirect('accounts:verify_master_password')
    except MasterPassword.DoesNotExist:
        pass

    if request.method == 'POST':
        form = MasterPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            master_pwd = MasterPassword(user=request.user)
            master_pwd.set_password(password)
            # Store in session for immediate verification
            request.session['master_password'] = password
            request.session['master_password_verified'] = True
            messages.success(request, "Master password set successfully!")
            return redirect('vault:dashboard')
    else:
        form = MasterPasswordForm()

    return render(request, 'accounts/setup_master_password.html', {'form': form})


@require_http_methods(["GET", "POST"])
def verify_master_password(request):
    """
    Verify master password to unlock the vault.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    try:
        master_pwd = MasterPassword.objects.get(user=request.user)
    except MasterPassword.DoesNotExist:
        return redirect('accounts:setup_master_password')

    # Check if already verified in this session
    try:
        session = UserSession.objects.get(user=request.user)
        if session.is_authenticated:
            return redirect('vault:dashboard')
    except UserSession.DoesNotExist:
        pass

    if request.method == 'POST':
        form = MasterPasswordVerifyForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if master_pwd.verify_password(password):
                # Create or update session
                session, created = UserSession.objects.get_or_create(user=request.user)
                session.is_authenticated = True
                session.save()
                # Store master password in session for encryption/decryption
                request.session['master_password'] = password
                request.session['master_password_verified'] = True
                messages.success(request, "Master password verified!")
                return redirect('vault:dashboard')
            else:
                messages.error(request, "Incorrect master password.")
    else:
        form = MasterPasswordVerifyForm()

    return render(request, 'accounts/verify_master_password.html', {'form': form})


@login_required
def logout_view(request):
    """
    Logout and clear session authentication.
    """
    # Clear master password from session
    if 'master_password' in request.session:
        del request.session['master_password']
    if 'master_password_verified' in request.session:
        del request.session['master_password_verified']
    
    try:
        session = UserSession.objects.get(user=request.user)
        session.is_authenticated = False
        session.save()
    except UserSession.DoesNotExist:
        pass

    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')


def register(request):
    """
    Simple user registration (for development).
    In production, you might want to restrict this.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('accounts:register')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:register')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return redirect('accounts:register')

        user = User.objects.create_user(username=username, password=password)
        messages.success(request, "Registration successful! Please log in.")
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')


def login_view(request):
    """
    Standard Django login view.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('accounts:verify_master_password')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')
