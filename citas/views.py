from django.shortcuts import render, redirect, get_object_or_404
from .models import Cita
from pacientes.models import Paciente
from doctores.models import Doctor


def lista_citas(request):

    q = request.GET.get('q')

    citas = Cita.objects.all().order_by('-fecha')

    if q:
        citas = citas.filter(paciente__nombre__icontains=q)

    return render(request, 'citas/lista.html', {
        'citas': citas
    })


def ver_cita(request, id):
    cita = get_object_or_404(Cita, id=id)

    return render(request, 'citas/ver.html', {
        'cita': cita
    })


def nueva_cita(request):

    pacientes = Paciente.objects.all()
    doctores = Doctor.objects.all()

    if request.method == 'POST':

        Cita.objects.create(
            paciente_id=request.POST['paciente'],
            doctor_id=request.POST['doctor'],
            fecha=request.POST['fecha'],
            hora=request.POST['hora'],
            motivo=request.POST['motivo'],
            estado="Pendiente"
        )

        return redirect('/citas/')

    return render(request, 'citas/nuevo.html', {
        'pacientes': pacientes,
        'doctores': doctores
    })


def editar_cita(request, id):

    cita = get_object_or_404(Cita, id=id)
    pacientes = Paciente.objects.all()
    doctores = Doctor.objects.all()

    if request.method == 'POST':

        cita.paciente_id = request.POST['paciente']
        cita.doctor_id = request.POST['doctor']
        cita.fecha = request.POST['fecha']
        cita.hora = request.POST['hora']
        cita.motivo = request.POST['motivo']
        cita.estado = request.POST['estado']

        cita.save()

        return redirect('/citas/')

    return render(request, 'citas/editar.html', {
        'cita': cita,
        'pacientes': pacientes,
        'doctores': doctores
    })


def eliminar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    cita.delete()
    return redirect('/citas/')