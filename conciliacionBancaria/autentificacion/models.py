from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

class CustomUserManager(BaseUserManager):
    """
    MANAGER/ADMIN -> creación y gestión de usuarios y superusuarios
    """
    def create_user(self, idusuario, nombre, apellido, role, password=None, **extra_fields):
        # Validaciones mínimas
        if not idusuario:
            raise ValueError("El idusuario es obligatorio")
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if not apellido:
            raise ValueError("El apellido es obligatorio")

        # Se crea la instancia del usuario
        user = self.model(
            idusuario=idusuario,
            nombre=nombre,
            apellido=apellido,
            role=role,
            **extra_fields
        )
        # Se encripta la contraseña
        user.set_password(password)
        # Se guarda en la base de datos
        user.save(using=self._db)
        return user

    def create_superuser(self, idusuario, nombre, apellido, password, **extra_fields):
        """
        Para crear un superusuario, se fuerza que:
         - role sea 'admin'
         - is_staff sea True
         - is_superuser sea True
        """
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('role') != 'admin':
            raise ValueError('El superusuario debe tener el rol "admin"')

        return self.create_user(
            idusuario, nombre, apellido, password=password, **extra_fields
        )

class User(AbstractBaseUser, PermissionsMixin):
    """
    USER -> modelo de usuario personalizado, hereda
    - AbstractBaseUser: para la parte de credenciales y métodos de autenticación.
    - PermissionsMixin: para integrar permisos y grupos de Django.
    """
    ROLE_CHOICES = [
        ('contador', 'Contador'),
        ('conciliador', 'Conciliador'),
        ('auditor', 'Auditor'),
        ('gerente', 'Gerente'),
    ]

    idusuario = models.CharField(max_length=50, unique=True, verbose_name="ID de Usuario", default="0")
    nombre = models.CharField(max_length=150, verbose_name="Nombre", default="N/A")
    apellido = models.CharField(max_length=150, verbose_name=" Apellido", default="N/A")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Rol", default="N/A")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico", blank=True, null=True , default="N/A") 
    # Campos administrativos
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Sobrescribimos groups y user_permissions para evitar conflictos con el modelo auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name="custom_user_set",
        help_text="Grupos a los que pertenece este usuario.",
        verbose_name="groups"
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name="custom_user_permissions_set",
        help_text="Permisos específicos para este usuario.",
        verbose_name="user permissions"
    )

    # Usamos el manager personalizado
    objects = CustomUserManager()

    # Informamos a Django que el campo para iniciar sesión será 'idusuario'
    USERNAME_FIELD = 'idusuario'
    
    # Campos obligatorios adicionales para crear un superusuario por línea de comandos (createsuperuser)
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def clean(self):
        super().clean()
        # Validación ejemplar del campo role (si no quieres permitir 'N/A')
        if self.role == 'N/A':
            raise ValidationError("Debes seleccionar un rol válido.")

        # Validación del correo (si no quieres permitir 'N/A')
        if self.email == 'N/A' or self.email is None:
            raise ValidationError("Debes indicar un correo electrónico válido.")
        
        # Validaciones para nombre y apellido
        if not self.nombre or self.nombre == 'N/A':
            raise ValidationError("El nombre no puede ser vacío o 'N/A'.")
        if not self.apellido or self.apellido == 'N/A':
            raise ValidationError("El apellido no puede ser vacío o 'N/A'.")

    def __str__(self):
        return f"{self.idusuario} - {self.nombre} {self.apellido} ({self.get_role_display()})"
