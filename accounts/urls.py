from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('cambiar-password/', views.cambiar_password),
    path('recuperar/', views.recuperar_password),
]