from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home, logout_view, register
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='autenticacion/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home, name='home'),
    path('register/', register, name='register'),  # <-- Nueva ruta

]
