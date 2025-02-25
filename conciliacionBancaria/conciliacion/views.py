import os
import csv
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Cuenta, Transaccion, TransaccionBancarias, TransaccionContables
from .forms import CuentaForm, TransaccionForm, UploadFileForm
from .serializers import CuentaSerializer,  TransaccionSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from dateutil.parser import parse as parse_datetime
from django_filters import rest_framework as filters
from django.views.generic import ListView
from django.db.models import Sum, Case, When, F, FloatField

# Definir la ruta para almacenar el archivo Excel de movimientos
EXCEL_FILE_PATH = os.path.join(settings.MEDIA_ROOT, 'movimientos.xlsx')

@login_required
def dashboard(request):
    # Obtén las cuentas del usuario
    cuentas = Cuenta.objects.filter(usuario=request.user)
    # Obtén transacciones donde el usuario es dueño de la cuenta de origen o destino
    transacciones = Transaccion.objects.filter(
        cuenta_origen__usuario=request.user
    ) | Transaccion.objects.filter(
        cuenta_destino__usuario=request.user
    )
    transacciones = transacciones.order_by('-fecha')
    context = {
        'cuentas': cuentas,
        'transacciones': transacciones,
    }
    return render(request, 'conciliacion/dashboard.html', context)

@login_required
def crear_cuenta(request):
    if request.method == 'POST':
        form = CuentaForm(request.POST)
        if form.is_valid():
            cuenta = form.save(commit=False)
            cuenta.usuario = request.user
            cuenta.save()
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('dashboard')
    else:
        form = CuentaForm()
    return render(request, 'conciliacion/crear_cuenta.html', {'form': form})

@login_required
def crear_transaccion(request):

    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            transaccion = form.save(commit=False)
            # Se pueden agregar validaciones adicionales si es necesario
            transaccion.save()
            messages.success(request, "Transacción creada exitosamente.")
            return redirect('dashboard')
    else:
        form = TransaccionForm()
    return render(request, 'conciliacion/crear_transaccion.html', {'form': form})

@login_required
def upload_csv(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            # Se decodifica el archivo CSV (asumiendo codificación UTF-8)
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                # Se espera que el CSV tenga las columnas: 'cuenta_id', 'tipo' y 'monto'
                cuenta_id = row.get('cuenta_id')
                tipo = row.get('tipo')
                monto = row.get('monto')
                
                # Valida que se hayan recibido todos los datos necesarios
                if not (cuenta_id and tipo and monto):
                    continue  # o podrías registrar el error en un log
                
                # Busca la cuenta correspondiente. Se podría hacer con un try/except para manejar errores.
                cuenta = get_object_or_404(Cuenta, id=cuenta_id)
                
                # Crea la transacción
                transaccion = Transaccion(
                    cuenta=cuenta,
                    tipo=tipo,
                    monto=monto
                )
                transaccion.save()
            # Redirecciona a alguna vista (por ejemplo, la lista de transacciones)
            return redirect('lista_transacciones')
    else:
        form = UploadFileForm()
    return render(request, 'upload_csv.html', {'form': form})

class CargarTransaccionesView(APIView):
    def post(self, request, *args, **kwargs):
        # Verificar si se envió un archivo
        if 'file' not in request.FILES:
            return Response({"error": "No se proporcionó ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)

        transacciones_creadas = 0
        errores = []

        for row in reader:
            try:
                # Extraer los datos de la fila
                cuenta_origen_id = int(row[0])
                cuenta_destino_id = int(row[1])
                monto = float(row[2])
                tipo = row[3]
                fecha_str = row[4]

                # Convertir la fecha a un objeto datetime
                fecha = parse_datetime(fecha_str)

                # Obtener las cuentas de origen y destino
                cuenta_origen = Cuenta.objects.get(id=cuenta_origen_id)
                cuenta_destino = Cuenta.objects.get(id=cuenta_destino_id)

                # Crear la transacción
                TransaccionBancarias.objects.create(
                    cuenta_origen=cuenta_origen,
                    cuenta_destino=cuenta_destino,
                    monto=monto,
                    tipo=tipo,
                    fecha=fecha
                )

                transacciones_creadas += 1
            except Cuenta.DoesNotExist:
                errores.append(f"Cuenta no encontrada en la fila: {row}")
            except Exception as e:
                errores.append(f"Error en la fila {row}: {str(e)}")

        if errores:
            return Response({
                "transacciones_creadas": transacciones_creadas,
                "errores": errores
            }, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({
                "transacciones_creadas": transacciones_creadas,
                "mensaje": "Todas las transacciones fueron creadas exitosamente."
            }, status=status.HTTP_201_CREATED)

class CargarTransaccionesEmpresaView(APIView):
    def post(self, request, *args, **kwargs):
        # Verificar si se envió un archivo
        if 'file' not in request.FILES:
            return Response({"error": "No se proporcionó ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)

        transacciones_creadas = 0
        errores = []

        for row in reader:
            try:
                # Extraer los datos de la fila
                cuenta_origen_id = int(row[0])
                cuenta_destino_id = int(row[1])
                monto = float(row[2])
                tipo = row[3]
                fecha_str = row[4]

                # Convertir la fecha a un objeto datetime
                fecha = parse_datetime(fecha_str)

                # Obtener las cuentas de origen y destino
                cuenta_origen = Cuenta.objects.get(id=cuenta_origen_id)
                cuenta_destino = Cuenta.objects.get(id=cuenta_destino_id)

                # Crear la transacción
                TransaccionContables.objects.create(
                    cuenta_origen=cuenta_origen,
                    cuenta_destino=cuenta_destino,
                    monto=monto,
                    tipo=tipo,
                    fecha=fecha
                )

                transacciones_creadas += 1
            except Cuenta.DoesNotExist:
                errores.append(f"Cuenta no encontrada en la fila: {row}")
            except Exception as e:
                errores.append(f"Error en la fila {row}: {str(e)}")

        if errores:
            return Response({
                "transacciones_creadas": transacciones_creadas,
                "errores": errores
            }, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({
                "transacciones_creadas": transacciones_creadas,
                "mensaje": "Todas las transacciones fueron creadas exitosamente."
            }, status=status.HTTP_201_CREATED)

class CuentaListCreateView(generics.ListCreateAPIView):
    queryset = Cuenta.objects.all()
    serializer_class = CuentaSerializer

class CuentaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cuenta.objects.all()
    serializer_class = CuentaSerializer

class TransaccionListView(ListView):
    model = TransaccionBancarias
    template_name = 'conciliacion/transacciones.html'  # Ruta del template
    context_object_name = 'transacciones'  # Nombre de la variable de contexto

class TransaccionBancoListView(ListView):
    model = TransaccionContables
    template_name = 'conciliacion/transaccionesEmpresariales.html'  # Ruta del template
    context_object_name = 'transaccionesBancarias'  # Nombre de la variable de contexto

def transacciones_agrupadas_view(request):
    # Agrupar las transacciones bancarias con signo condicional
    transacciones_agrupadas = TransaccionBancarias.objects.values('tipo').annotate(
        total=Sum(
            Case(
                When(tipo='retiro', then=-F('monto')),
                When(tipo__in=['deposito', 'transferencia'], then=F('monto')),
                default=F('monto'),
                output_field=FloatField()
            )
        )
    )

    # Agrupar las transacciones empresariales con la misma lógica
    transacciones_agrupadas_empresariales = TransaccionContables.objects.values('tipo').annotate(
        total=Sum(
            Case(
                When(tipo='retiro', then=-F('monto')),
                When(tipo__in=['deposito', 'transferencia'], then=F('monto')),
                default=F('monto'),
                output_field=FloatField()
            )
        )
    )

    # Calcular totales
    total_bancarias = sum(item['total'] for item in transacciones_agrupadas)
    total_empresariales = sum(item['total'] for item in transacciones_agrupadas_empresariales)
    descuadre = total_bancarias - total_empresariales

    context = {
        'transacciones_agrupadas': transacciones_agrupadas, 
        'transacciones_agrupadas_empresariales': transacciones_agrupadas_empresariales,
        'total_bancarias': total_bancarias,
        'total_empresariales': total_empresariales,
        'descuadre': descuadre,
    }
    return render(request, 'conciliacion/transacciones_agrupadas.html', context)