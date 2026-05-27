from django.shortcuts import render
from datetime import date

from django.contrib.auth.decorators import login_required, user_passes_test

from pacientes.models import Paciente
from doctores.models import Doctor
from citas.models import Cita
from resultados.models import Resultado


def es_personal(user):
    # si el usuario NO es paciente -> es personal
    return not Paciente.objects.filter(usuario=user).exists()


@login_required
@user_passes_test(es_personal, login_url='/portal/')
def dashboard(request):

    # Totales
    total_pacientes = Paciente.objects.count()
    total_doctores = Doctor.objects.count()
    total_resultados = Resultado.objects.count()

    # Citas de hoy
    citas_hoy_lista = Cita.objects.filter(
        fecha=date.today()
    ).select_related(
        'paciente',
        'doctor'
    ).order_by('hora')

    citas_hoy = citas_hoy_lista.count()

    # Últimos resultados
    resultados_lista = Resultado.objects.select_related(
        'paciente',
        'doctor'
    ).order_by('-fecha')[:5]

    # contador menu
    citas_hoy_menu = citas_hoy

    return render(request, 'dashboard.html', {
        'total_pacientes': total_pacientes,
        'total_doctores': total_doctores,
        'citas_hoy': citas_hoy,
        'total_resultados': total_resultados,
        'citas_lista': citas_hoy_lista,
        'resultados_lista': resultados_lista,
        'citas_hoy_menu': citas_hoy_menu
    })