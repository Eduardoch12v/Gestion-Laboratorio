from django.db import models

class Doctor(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    consultorio = models.CharField(max_length=20)

    estado = models.CharField(
        max_length=20,
        choices=[
            ('Activo', 'Activo'),
            ('Inactivo', 'Inactivo'),
            ('Vacaciones', 'Vacaciones')
        ],
        default='Activo'
    )

    def __str__(self):
        return self.nombre