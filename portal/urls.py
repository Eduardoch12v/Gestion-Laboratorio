from django.urls import path
from .views import portal_dashboard, descargar_pdf, exportar_citas_pdf

urlpatterns = [
    path('', portal_dashboard, name='portal'),
    path('pdf/', descargar_pdf, name='portal_pdf'),
    path('citas/pdf/', exportar_citas_pdf, name='citas_pdf'),
]