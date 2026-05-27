from django.db import models
from pacientes.models import Paciente
from doctores.models import Doctor

class Cita(models.Model):

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    fecha = models.DateField()
    hora = models.TimeField()

    motivo = models.CharField(max_length=255)

    estado = models.CharField(
        max_length=20,
        default="Pendiente"
    )

    def __str__(self):
        return f"{self.paciente} - {self.fecha}"