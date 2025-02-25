from django.urls import path
from . import views
from .views import CuentaListCreateView, CuentaRetrieveUpdateDestroyView, CargarTransaccionesView, TransaccionListView, CargarTransaccionesEmpresaView, TransaccionBancoListView, transacciones_agrupadas_view

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('crear_cuenta/', views.crear_cuenta, name='crear_cuenta'),
    path('crear_transaccion/', views.crear_transaccion, name='crear_transaccion'),
    
    # Ruta para listar y crear cuentas
    path('cuentas/', CuentaListCreateView.as_view(), name='cuenta-list-create'),

    # Ruta para cargar transacciones desde un archivo Excel
    path('cargar-transacciones-banco/', CargarTransaccionesView.as_view(), name='cargar_transacciones_banco'),
    path('cargar-transacciones-empresa/', CargarTransaccionesEmpresaView.as_view(), name='cargar_transacciones_empresa'),

    # Ruta para listar transacciones
    path('transaccionesEmpresa/', TransaccionListView.as_view(), name='transaccion-list-empresa'),
    path('transaccionesBancarias/', TransaccionBancoListView.as_view(), name='transaccion-list-banco'),

    path('transacciones-agrupadas/', transacciones_agrupadas_view, name='transacciones-agrupadas'),

    # Ruta para recuperar, actualizar y eliminar una cuenta específica
    path('cuentas/<int:pk>/', CuentaRetrieveUpdateDestroyView.as_view(), name='cuenta-retrieve-update-destroy'),
]