"""
URL routing for vault app
"""

from django.urls import path
from . import views

app_name = 'vault'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('credential/<int:pk>/', views.credential_detail, name='credential_detail'),
    path('credential/create/', views.create_credential, name='create_credential'),
    path('credential/<int:pk>/edit/', views.edit_credential, name='edit_credential'),
    path('credential/<int:pk>/delete/', views.delete_credential, name='delete_credential'),
    path('password-generator/', views.password_generator, name='password_generator'),
    path('api/copy-log/<int:pk>/', views.copy_to_clipboard_log, name='copy_log'),
    path('api/password-check/', views.password_check, name='password_check'),
]
