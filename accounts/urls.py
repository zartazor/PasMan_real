"""
URL routing for accounts app
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('setup-master-password/', views.setup_master_password, name='setup_master_password'),
    path('verify-master-password/', views.verify_master_password, name='verify_master_password'),
]
