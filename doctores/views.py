from django.shortcuts import render, redirect, get_object_or_404
from .models import Doctor
from django.db.models import Q
from django.contrib import messages
import re


def lista_doctores(request):
    buscar = request.GET.get('buscar')

    doctores = Doctor.objects.all()

    if buscar:
        doctores = doctores.filter(
            Q(nombre__icontains=buscar) |
            Q(especialidad__icontains=buscar)
        )

    total = Doctor.objects.count()
    activos = Doctor.objects.filter(estado='Activo').count()
    especialidades = Doctor.objects.values('especialidad').distinct().count()

    context = {
        'doctores': doctores,
        'total': total,
        'activos': activos,
        'especialidades': especialidades
    }

    return render(request, 'doctores/lista.html', context)


def nuevo_doctor(request):
    if request.method == 'POST':

        try:
            nombre = request.POST.get('nombre')
            especialidad = request.POST.get('especialidad')
            telefono = request.POST.get('telefono')
            consultorio = request.POST.get('consultorio')

            # VALIDACIONES
            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', nombre):
                messages.error(request, "Nombre inválido")
                return redirect(request.path)

            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', especialidad):
                messages.error(request, "Especialidad inválida")
                return redirect(request.path)

            if telefono and not telefono.isdigit():
                messages.error(request, "Teléfono inválido")
                return redirect(request.path)

            # consultorio tipo A45, B12
            if consultorio and not re.match(r'^[A-Za-z0-9]+$', consultorio):
                messages.error(request, "Consultorio inválido")
                return redirect(request.path)

            Doctor.objects.create(
                nombre=nombre,
                especialidad=especialidad,
                telefono=telefono,
                consultorio=consultorio,
                estado=request.POST.get('estado', 'Activo')
            )

            messages.success(request, "Doctor registrado correctamente")

            return redirect('/doctores/')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect(request.path)

    return render(request, 'doctores/nuevo.html')


def editar_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)

    if request.method == 'POST':

        try:
            nombre = request.POST.get('nombre')
            especialidad = request.POST.get('especialidad')
            telefono = request.POST.get('telefono')
            consultorio = request.POST.get('consultorio')

            # VALIDACIONES
            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', nombre):
                messages.error(request, "Nombre inválido")
                return redirect(request.path)

            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', especialidad):
                messages.error(request, "Especialidad inválida")
                return redirect(request.path)

            if telefono and not telefono.isdigit():
                messages.error(request, "Teléfono inválido")
                return redirect(request.path)

            if consultorio and not re.match(r'^[A-Za-z0-9]+$', consultorio):
                messages.error(request, "Consultorio inválido")
                return redirect(request.path)

            doctor.nombre = nombre
            doctor.especialidad = especialidad
            doctor.telefono = telefono
            doctor.consultorio = consultorio
            doctor.estado = request.POST.get('estado', 'Activo')

            doctor.save()

            messages.success(request, "Doctor actualizado correctamente")

            return redirect('/doctores/')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect(request.path)

    return render(request, 'doctores/editar.html', {'doctor': doctor})


def eliminar_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    doctor.delete()

    messages.success(request, "Doctor eliminado correctamente")

    return redirect('/doctores/')


def ver_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    return render(request, 'doctores/ver.html', {'doctor': doctor})