from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages

from pacientes.models import Paciente


@login_required
def panel_admin(request):
    return render(request,'administrador/panel.html')


@login_required
def usuarios(request):

    usuarios = User.objects.all()

    return render(request,'administrador/usuarios.html',{
        'usuarios':usuarios
    })


@login_required
def crear_usuario(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        rol = request.POST.get('rol')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        grupo, created = Group.objects.get_or_create(name=rol)
        user.groups.add(grupo)

        messages.success(request,"Usuario creado correctamente")

        return redirect('/administrador/usuarios/')

    return render(request,'administrador/crear.html')


@login_required
def eliminar_usuario(request,id):

    user = get_object_or_404(User,id=id)

    # eliminar paciente ligado si existe
    Paciente.objects.filter(usuario=user).delete()

    user.delete()

    messages.success(request,"Usuario eliminado correctamente")

    return redirect('/administrador/usuarios/')


@login_required
def toggle_usuario(request,id):

    user = get_object_or_404(User,id=id)

    user.is_active = not user.is_active
    user.save()

    return redirect('/administrador/usuarios/')


@login_required
def reset_password(request,id):

    user = get_object_or_404(User,id=id)

    user.set_password("123456")
    user.save()

    messages.success(
        request,
        f"Password de {user.username} reseteado a 123456"
    )

    return redirect('/administrador/usuarios/')