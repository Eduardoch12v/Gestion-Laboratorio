from django.urls import path
from usuarios.views import dashboard_personal

urlpatterns = [
    path('personal/', dashboard_personal, name='dashboard_personal'),
]