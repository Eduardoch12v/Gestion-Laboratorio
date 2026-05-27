from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('paciente/', views.dashboard_paciente, name='dashboard_paciente'),
]