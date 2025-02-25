from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Cuenta(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cuentas"
    )
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    moneda = models.CharField(max_length=3, default="USD")

    def __str__(self):
        return f"{self.usuario.username} - {self.saldo} {self.moneda}"

class Transaccion(models.Model):
    TIPO_TRANSACCION = [
        ('DEP', 'Depósito'),
        ('RET', 'Retiro'),
        ('TRA', 'Transferencia')
    ]

    cuenta_origen = models.ForeignKey(
        Cuenta,
        on_delete=models.CASCADE,
        related_name="transacciones_enviadas",
        null=True,
        blank=True
    )
    cuenta_destino = models.ForeignKey(
        Cuenta,
        on_delete=models.CASCADE,
        related_name="transacciones_recibidas",
        null=True,
        blank=True
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=3, choices=TIPO_TRANSACCION)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.monto} - {self.fecha}"

class MovimientoBancario(models.Model):
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    referencia = models.CharField(max_length=100, blank=True, null=True)

    # Este campo ayuda a identificar si está conciliado o no
    conciliado = models.BooleanField(default=False)
    # Relación con usuario que lo cargó, si aplica
    user = models.ForeignKey('autentificacion.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.fecha} - {self.descripcion} - {self.monto}"