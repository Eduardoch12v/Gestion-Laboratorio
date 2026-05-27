from django.urls import path
from . import views

urlpatterns = [

path('', views.lista_resultados),
path('nuevo/', views.nuevo_resultado),
path('ver/<int:id>/', views.ver_resultado),
path('editar/<int:id>/', views.editar_resultado),
path('eliminar/<int:id>/', views.eliminar_resultado),

# PDF
path('pdf/<int:id>/', views.pdf_resultado),

]