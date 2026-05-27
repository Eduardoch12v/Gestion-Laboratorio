from django.urls import path
from . import views

urlpatterns = [

    path('', views.panel_admin),
    path('usuarios/', views.usuarios),

    path('crear/', views.crear_usuario),

    path('eliminar/<int:id>/', views.eliminar_usuario),
    path('toggle/<int:id>/', views.toggle_usuario),
    path('reset/<int:id>/', views.reset_password),

]