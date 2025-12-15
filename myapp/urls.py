from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('health/', views.health_check, name='health_check'),
    path('api/status/', views.api_status, name='api_status'),
]