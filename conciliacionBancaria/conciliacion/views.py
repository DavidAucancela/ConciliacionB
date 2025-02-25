import os
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Cuenta, Transaccion, MovimientoBancario
from .forms import CuentaForm, TransaccionForm, UploadFileForm
from django.core.files.storage import FileSystemStorage

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
def cargar_archivos(request):
    """
    Vista para cargar un archivo Excel, guardarlo en el servidor y registrar movimientos en la base de datos.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                # Guardar el archivo de forma permanente
                fs = FileSystemStorage()
                filename = fs.save(excel_file.name, excel_file)
                file_url = fs.url(filename)

                # Leer el archivo con pandas (puedes usar la ruta o directamente el objeto)
                df = pd.read_excel(excel_file)

                # Validar columnas esperadas
                expected_columns = {'date', 'description', 'amount'}
                if not expected_columns.issubset(df.columns):
                    messages.error(request, "El archivo Excel debe contener las columnas: date, description, amount.")
                    return redirect('upload_excel')

                # (Opcional) Guardar el DataFrame a otro archivo o ruta, si es necesario
                df.to_excel(EXCEL_FILE_PATH, index=False)

                # Registrar movimientos en la base de datos
                for _, row in df.iterrows():
                    MovimientoBancario.objects.create(
                        user=request.user,
                        date=row['date'],
                        description=row['description'],
                        amount=row['amount']
                    )

                messages.success(request, "Archivo Excel cargado y movimientos registrados correctamente.")
                return redirect('conciliar')
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo Excel: {e}")
    else:
        form = UploadFileForm()
    
    return render(request, 'conciliacion/upload_excel.html', {'form': form})

@login_required
def conciliar(request):
    """
    Vista que muestra los movimientos cargados desde el archivo Excel.
    Permite editar y actualizar los datos.
    """
    movimientos = []
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        movimientos = df.to_dict(orient='records')
    except FileNotFoundError:
        messages.info(request, "No se ha cargado ningún archivo Excel.")
    except Exception as e:
        messages.error(request, f"Error al leer el archivo Excel: {e}")

    return render(request, 'conciliacion/conciliar.html', {'movimientos': movimientos})

@login_required
@require_http_methods(["POST"])
def registrar_movimiento(request):
    """
    Vista para agregar un nuevo movimiento y actualizar el archivo Excel.
    """
    date = request.POST.get('date')
    description = request.POST.get('description')
    amount = request.POST.get('amount')

    if not all([date, description, amount]):
        messages.error(request, "Todos los campos son requeridos.")
        return redirect('conciliar')

    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'description', 'amount'])
    except Exception as e:
        messages.error(request, f"Error al leer el archivo Excel: {e}")
        return redirect('conciliar')

    new_movement = {'date': date, 'description': description, 'amount': amount}
    df = df.append(new_movement, ignore_index=True)

    try:
        df.to_excel(EXCEL_FILE_PATH, index=False)
        MovimientoBancario.objects.create(
            user=request.user,
            date=date,
            description=description,
            amount=amount
        )
        messages.success(request, "Movimiento registrado exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al guardar el movimiento: {e}")

    return redirect('conciliar')

@login_required
@require_http_methods(["POST"])
def actualizar_movimiento(request, row_index):
    """
    Vista para actualizar un movimiento en el archivo Excel y la base de datos.
    """
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        if row_index >= len(df):
            messages.error(request, "Índice inválido de movimiento.")
            return redirect('conciliar')

        df.loc[row_index, 'date'] = request.POST.get('date')
        df.loc[row_index, 'description'] = request.POST.get('description')
        df.loc[row_index, 'amount'] = request.POST.get('amount')

        df.to_excel(EXCEL_FILE_PATH, index=False)

        movimiento = MovimientoBancario.objects.filter(user=request.user)[row_index]
        movimiento.date = request.POST.get('date')
        movimiento.description = request.POST.get('description')
        movimiento.amount = request.POST.get('amount')
        movimiento.save()

        messages.success(request, "Movimiento actualizado exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al actualizar el movimiento: {e}")

    return redirect('conciliar')

@login_required
@require_http_methods(["POST"])
def eliminar_movimiento(request, row_index):
    """
    Vista para eliminar un movimiento en el archivo Excel y la base de datos.
    """
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        if row_index >= len(df):
            messages.error(request, "Índice inválido de movimiento.")
            return redirect('conciliar')

        df.drop(index=row_index, inplace=True)
        df.to_excel(EXCEL_FILE_PATH, index=False)

        movimiento = MovimientoBancario.objects.filter(user=request.user)[row_index]
        movimiento.delete()

        messages.success(request, "Movimiento eliminado exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar el movimiento: {e}")

    return redirect('conciliar')

@login_required
def mostrar_movimientos(request):
    """
    Vista para mostrar los movimientos almacenados en la base de datos.
    """
    movimientos = MovimientoBancario.objects.filter(user=request.user)
    return render(request, 'conciliacion/mostrar_movimientos.html', {'movimientos': movimientos})