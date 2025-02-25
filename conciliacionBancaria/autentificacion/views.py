from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from django.contrib import messages

@login_required
def home(request):
    return render(request, 'autenticacion/home.html')

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # se crea el usuario en la BD
            # Opcional: inicias sesión automáticamente al nuevo usuario
            # login(request, user)
            messages.success(request, "¡Usuario creado exitosamente!")
            return redirect('home')  # redirige a donde quieras
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'autenticacion/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')
