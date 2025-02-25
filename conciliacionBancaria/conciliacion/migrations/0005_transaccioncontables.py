# Generated by Django 5.1.6 on 2025-02-25 07:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conciliacion', '0004_remove_transaccion_cuenta_transaccion_cuenta_destino_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransaccionContables',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipo', models.CharField(choices=[('DEP', 'Depósito'), ('RET', 'Retiro'), ('TRA', 'Transferencia')], max_length=3)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('cuenta_destino', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transacciones_contable_recibidas', to='conciliacion.cuenta')),
                ('cuenta_origen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transacciones_contable_enviadas', to='conciliacion.cuenta')),
            ],
        ),
    ]
