from django.urls import path
from . import views

urlpatterns = [

path('', views.lista_citas),
path('nuevo/', views.nueva_cita),
path('ver/<int:id>/', views.ver_cita),
path('editar/<int:id>/', views.editar_cita),
path('eliminar/<int:id>/', views.eliminar_cita),

]