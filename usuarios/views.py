from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.groups.filter(name='Personal').exists():
                return redirect('dashboard_personal')

            elif user.groups.filter(name='Paciente').exists():
                return redirect('dashboard_paciente')

        else:
            return render(request, 'usuarios/login.html', {'error': 'Usuario incorrecto'})

    return render(request, 'usuarios/login.html')


@login_required
def dashboard_personal(request):
    return render(request, 'personal/dashboard_personal.html')


@login_required
def dashboard_paciente(request):
    return render(request, 'usuarios/dashboard_paciente.html')