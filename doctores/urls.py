from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_doctores),
    path('nuevo/', views.nuevo_doctor),
    path('editar/<int:id>/', views.editar_doctor),
    path('eliminar/<int:id>/', views.eliminar_doctor),
    path('ver/<int:id>/', views.ver_doctor),
]