from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente
from django.contrib import messages
from citas.models import Cita
from resultados.models import Resultado
from django.contrib.auth.models import User, Group
import re


def lista_pacientes(request):

    buscar = request.GET.get('buscar')

    if buscar:
        pacientes = Paciente.objects.filter(
            nombre__icontains=buscar
        ) | Paciente.objects.filter(
            apellido__icontains=buscar
        )
    else:
        pacientes = Paciente.objects.all()

    total = Paciente.objects.count()

    return render(request, 'pacientes/lista.html', {
        'pacientes': pacientes,
        'total': total
    })


def nuevo_paciente(request):

    if request.method == 'POST':

        try:
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            telefono = request.POST.get('telefono')
            correo = request.POST.get('correo')
            genero = request.POST.get('genero') or "No especificado"
            direccion = request.POST.get('direccion') or ""

            tipo_sangre = request.POST.get('tipo_sangre')
            contacto_emergencia = request.POST.get('contacto_emergencia')

            # VALIDACIONES
            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', nombre):
                messages.error(request, "Nombre inválido")
                return redirect(request.path)

            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', apellido):
                messages.error(request, "Apellido inválido")
                return redirect(request.path)

            if telefono and not telefono.isdigit():
                messages.error(request, "Teléfono inválido")
                return redirect(request.path)

            if contacto_emergencia and not contacto_emergencia.isdigit():
                messages.error(request, "Contacto de emergencia inválido")
                return redirect(request.path)

            # CREAR USUARIO
            user = User.objects.create_user(
                username=correo,
                email=correo,
                password="123456"
            )

            grupo, created = Group.objects.get_or_create(name="Paciente")
            user.groups.add(grupo)

            # CREAR PACIENTE
            Paciente.objects.create(
                usuario=user,
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nacimiento,
                telefono=telefono,
                correo=correo,
                genero=genero,
                direccion=direccion,
                tipo_sangre=tipo_sangre,
                contacto_emergencia=contacto_emergencia
            )

            messages.success(
                request,
                "Paciente registrado correctamente"
            )

            return redirect('/pacientes/')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect(request.path)

    return render(request, 'pacientes/nuevo.html')


def editar_paciente(request, id):

    paciente = get_object_or_404(Paciente, id=id)

    if request.method == 'POST':

        try:
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            telefono = request.POST.get('telefono')
            contacto_emergencia = request.POST.get('contacto_emergencia')

            # VALIDACIONES
            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', nombre):
                messages.error(request, "Nombre inválido")
                return redirect(request.path)

            if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', apellido):
                messages.error(request, "Apellido inválido")
                return redirect(request.path)

            if telefono and not telefono.isdigit():
                messages.error(request, "Teléfono inválido")
                return redirect(request.path)

            if contacto_emergencia and not contacto_emergencia.isdigit():
                messages.error(request, "Contacto de emergencia inválido")
                return redirect(request.path)

            # ACTUALIZAR DATOS
            paciente.nombre = nombre
            paciente.apellido = apellido
            paciente.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            paciente.telefono = telefono
            paciente.correo = request.POST.get('correo')
            paciente.genero = request.POST.get('genero') or "No especificado"
            paciente.direccion = request.POST.get('direccion') or ""
            paciente.tipo_sangre = request.POST.get('tipo_sangre')
            paciente.contacto_emergencia = contacto_emergencia

            # ACTUALIZAR USUARIO
            if paciente.usuario:
                paciente.usuario.username = paciente.correo
                paciente.usuario.email = paciente.correo
                paciente.usuario.save()

            paciente.save()

            messages.success(
                request,
                "Paciente actualizado correctamente"
            )

            return redirect('/pacientes/')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect(request.path)

    return render(request, 'pacientes/editar.html', {
        'paciente': paciente
    })


def eliminar_paciente(request, id):

    paciente = get_object_or_404(Paciente, id=id)

    if paciente.usuario:
        paciente.usuario.delete()

    paciente.delete()

    messages.success(
        request,
        "Paciente eliminado correctamente"
    )

    return redirect('/pacientes/')


def ver_paciente(request, id):

    paciente = get_object_or_404(Paciente, id=id)

    citas = Cita.objects.filter(
        paciente=paciente
    ).order_by('-fecha')

    resultados = Resultado.objects.filter(
        paciente=paciente
    ).order_by('-fecha')

    return render(request, 'pacientes/ver.html', {
        'paciente': paciente,
        'citas': citas,
        'resultados': resultados
    })