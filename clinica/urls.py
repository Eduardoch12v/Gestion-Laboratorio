from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [

    path('', lambda request: redirect('/login/')),

    path('admin/', admin.site.urls),

    path('', include('accounts.urls')),

    path('dashboard/', include('dashboard.urls')),
    path('pacientes/', include('pacientes.urls')),
    path('doctores/', include('doctores.urls')),
    path('citas/', include('citas.urls')),
    path('resultados/', include('resultados.urls')),
    path('portal/', include('portal.urls')),
    path('administrador/', include('administrador.urls')),

]