"""
Views for the vault (password manager)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from accounts.models import MasterPassword, UserSession
from vault.models import Credential, AuditLog
from vault.forms import CredentialForm, PasswordGeneratorForm, SearchForm
from vault.encryption import encrypt_password, decrypt_password, derive_encryption_key
from vault.password_utils import PasswordGenerator, PasswordStrength


def require_master_password(view_func):
    """
    Decorator to ensure user has verified their master password.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        # Check if master password is verified in session
        if not request.session.get('master_password_verified', False):
            return redirect('accounts:verify_master_password')

        # Verify that master password exists in session
        if 'master_password' not in request.session:
            return redirect('accounts:verify_master_password')

        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@require_master_password
def dashboard(request):
    """
    Main vault dashboard showing all stored credentials.
    """
    credentials = Credential.objects.filter(user=request.user)
    search_form = SearchForm(request.GET)

    # Search and filter
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query', '')
        category = search_form.cleaned_data.get('category', '')

        if query:
            credentials = credentials.filter(
                Q(website_name__icontains=query) |
                Q(username__icontains=query) |
                Q(email__icontains=query)
            )

        if category:
            credentials = credentials.filter(category=category)

    # Get stats for dashboard
    total_credentials = Credential.objects.filter(user=request.user).count()
    categories = dict(Credential._meta.get_field('category').choices)

    context = {
        'credentials': credentials,
        'search_form': search_form,
        'total_credentials': total_credentials,
        'categories': categories,
    }

    return render(request, 'vault/dashboard.html', context)


@login_required
@require_master_password
def credential_detail(request, pk):
    """
    View details of a specific credential and show decrypted password.
    """
    credential = get_object_or_404(Credential, pk=pk, user=request.user)

    # Decrypt password
    try:
        master_pwd = MasterPassword.objects.get(user=request.user)
        master_password = request.session.get('master_password')
        
        if not master_password:
            messages.error(request, "Master password not found in session. Please verify again.")
            return redirect('accounts:verify_master_password')

        encryption_key = derive_encryption_key(master_password, master_pwd.salt)
        decrypted_password = decrypt_password(credential.encrypted_password, encryption_key)
        
        password_strength = None
        if decrypted_password:
            score, label, color = PasswordStrength.score(decrypted_password)
            password_strength = {
                'score': score,
                'label': label,
                'color': color,
                'max': 5
            }
    except Exception as e:
        messages.error(request, f"Could not decrypt password: {str(e)}")
        return redirect('vault:dashboard')

    # Log access
    AuditLog.objects.create(
        user=request.user,
        credential=credential,
        action='view',
        ip_address=get_client_ip(request)
    )

    context = {
        'credential': credential,
        'decrypted_password': decrypted_password,
        'password_strength': password_strength,
    }

    return render(request, 'vault/credential_detail.html', context)


@login_required
@require_master_password
def create_credential(request):
    """
    Create a new credential.
    """
    if request.method == 'POST':
        form = CredentialForm(request.POST)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.user = request.user

            # Encrypt password
            password = request.POST.get('password', '')
            if password:
                try:
                    master_pwd = MasterPassword.objects.get(user=request.user)
                    master_password = request.session.get('master_password')
                    
                    if not master_password:
                        messages.error(request, "Master password not verified. Please verify again.")
                        return redirect('accounts:verify_master_password')
                    
                    encryption_key = derive_encryption_key(master_password, master_pwd.salt)
                    credential.encrypted_password = encrypt_password(password, encryption_key)
                except MasterPassword.DoesNotExist:
                    messages.error(request, "Master password not found.")
                    return redirect('accounts:setup_master_password')
                except Exception as e:
                    messages.error(request, f"Could not encrypt password: {str(e)}")
                    return render(request, 'vault/create_credential.html', {'form': form})
            else:
                messages.warning(request, "Password field was empty.")

            credential.save()

            # Log action
            AuditLog.objects.create(
                user=request.user,
                credential=credential,
                action='create',
                ip_address=get_client_ip(request)
            )

            messages.success(request, f"Credential for {credential.website_name} created successfully!")
            return redirect('vault:dashboard')
    else:
        form = CredentialForm()

    return render(request, 'vault/create_credential.html', {'form': form})


@login_required
@require_master_password
def edit_credential(request, pk):
    """
    Edit an existing credential.
    """
    credential = get_object_or_404(Credential, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CredentialForm(request.POST, instance=credential)
        if form.is_valid():
            credential = form.save(commit=False)

            # Update encrypted password if provided
            password = request.POST.get('password', '')
            if password:
                try:
                    master_pwd = MasterPassword.objects.get(user=request.user)
                    master_password = request.session.get('master_password')
                    
                    if not master_password:
                        messages.error(request, "Master password not verified. Please verify again.")
                        return redirect('accounts:verify_master_password')
                    
                    encryption_key = derive_encryption_key(master_password, master_pwd.salt)
                    credential.encrypted_password = encrypt_password(password, encryption_key)
                except Exception as e:
                    messages.error(request, f"Could not encrypt password: {str(e)}")
                    return render(request, 'vault/edit_credential.html', {'form': form, 'credential': credential})

            credential.save()

            # Log action
            AuditLog.objects.create(
                user=request.user,
                credential=credential,
                action='edit',
                ip_address=get_client_ip(request)
            )

            messages.success(request, f"Credential for {credential.website_name} updated!")
            return redirect('vault:credential_detail', pk=credential.pk)
    else:
        form = CredentialForm(instance=credential)

    return render(request, 'vault/edit_credential.html', {'form': form, 'credential': credential})


@login_required
@require_master_password
def delete_credential(request, pk):
    """
    Delete a credential.
    """
    credential = get_object_or_404(Credential, pk=pk, user=request.user)

    if request.method == 'POST':
        website_name = credential.website_name

        # Log action
        AuditLog.objects.create(
            user=request.user,
            credential=credential,
            action='delete',
            ip_address=get_client_ip(request)
        )

        credential.delete()
        messages.success(request, f"Credential for {website_name} deleted.")
        return redirect('vault:dashboard')

    return render(request, 'vault/confirm_delete.html', {'credential': credential})


@require_http_methods(["GET"])
@login_required
def password_generator(request):
    """
    Password generator view.
    """
    form = PasswordGeneratorForm(request.GET)
    generated_password = None
    password_strength = None

    if form.is_valid():
        generated_password = PasswordGenerator.generate(
            length=form.cleaned_data['length'],
            uppercase=form.cleaned_data['uppercase'],
            lowercase=form.cleaned_data['lowercase'],
            numbers=form.cleaned_data['numbers'],
            symbols=form.cleaned_data['symbols'],
        )
        score, label, color = PasswordStrength.score(generated_password)
        password_strength = {
            'score': score,
            'label': label,
            'color': color,
            'max': 5
        }

    return render(request, 'vault/password_generator.html', {
        'form': form,
        'generated_password': generated_password,
        'password_strength': password_strength,
    })


@require_http_methods(["POST"])
@login_required
def copy_to_clipboard_log(request, pk):
    """
    API endpoint to log password/username copy events.
    """
    credential = get_object_or_404(Credential, pk=pk, user=request.user)
    action = request.POST.get('action', 'copy_password')

    if action not in ['copy_password', 'copy_username']:
        action = 'copy_password'

    AuditLog.objects.create(
        user=request.user,
        credential=credential,
        action=action,
        ip_address=get_client_ip(request)
    )

    return JsonResponse({'status': 'logged'})


@login_required
@require_master_password
def password_check(request):
    """
    Check password strength (AJAX endpoint).
    """
    password = request.GET.get('password', '')
    if not password:
        return JsonResponse({'error': 'No password provided'}, status=400)

    score, label, color = PasswordStrength.score(password)
    requirements = PasswordStrength.get_requirements_met(password)

    return JsonResponse({
        'score': score,
        'label': label,
        'color': color,
        'max': 5,
        'requirements': requirements,
    })


def get_client_ip(request):
    """
    Get client's IP address for audit logging.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
