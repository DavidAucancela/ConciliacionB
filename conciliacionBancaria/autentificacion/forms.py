from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User

class CustomAuthenticationForm(AuthenticationForm):
    # Se utiliza el campo 'idusuario' en lugar de 'username'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "ID de Usuario"

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('idusuario', 'nombre', 'apellido', 'role', 'email')
