from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pacientes),
    path('nuevo/', views.nuevo_paciente),
    path('editar/<int:id>/', views.editar_paciente),
    path('eliminar/<int:id>/', views.eliminar_paciente),
    path('ver/<int:id>/', views.ver_paciente),
]