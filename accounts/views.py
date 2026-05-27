from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):

    # si ya está logeado
    if request.user.is_authenticated:
        return redireccion_por_rol(request.user)

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        # 🔥 login con correo
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except:
                user = None

        if user is not None:

            login(request, user)

            return redireccion_por_rol(user)

        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'login.html')


# 🔥 FUNCIÓN CENTRAL (AQUÍ ESTÁ LA CLAVE)
def redireccion_por_rol(user):

    if user.is_superuser:
        return redirect('/administrador/')

    if user.groups.filter(name='Administrador').exists():
        return redirect('/administrador/')

    if user.groups.filter(name='Personal').exists():
        return redirect('/dashboard/')

    if user.groups.filter(name='Paciente').exists():
        return redirect('/portal/')

    # fallback
    return redirect('/dashboard/')


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def cambiar_password(request):

    if request.method == "POST":

        nueva = request.POST.get('password')

        user = request.user
        user.set_password(nueva)
        user.save()

        messages.success(request, "Contraseña actualizada")

        return redirect('/login/')

    return render(request, 'cambiar_password.html')


# 🔥 RECUPERAR PASSWORD
def recuperar_password(request):

    if request.method == "POST":

        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            user.set_password("123456")
            user.save()

            messages.success(
                request,
                "Contraseña reiniciada a: 123456"
            )

        except User.DoesNotExist:
            messages.error(
                request,
                "No existe un usuario con ese correo"
            )

    return render(request, 'recuperar.html')