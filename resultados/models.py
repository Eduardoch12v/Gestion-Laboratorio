from django.db import models
from pacientes.models import Paciente
from doctores.models import Doctor
from citas.models import Cita


class Resultado(models.Model):

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)

    diagnostico = models.TextField()
    observaciones = models.TextField(blank=True)

    fecha = models.DateField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        default="Completado"
    )

    def __str__(self):
        return str(self.paciente)