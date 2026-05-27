from django.db import models
from django.contrib.auth.models import User

class Paciente(models.Model):

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField()
    genero = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    
    tipo_sangre = models.CharField(max_length=5, blank=True, null=True)
    contacto_emergencia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"