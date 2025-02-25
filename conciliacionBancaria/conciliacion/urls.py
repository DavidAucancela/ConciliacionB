from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('crear_cuenta/', views.crear_cuenta, name='crear_cuenta'),
    path('crear_transaccion/', views.crear_transaccion, name='crear_transaccion'),
    path('cargar_archivos/', views.cargar_archivos, name='cargar_archivos'),
    path('conciliar/', views.conciliar, name='conciliar'),
    path('registrar_movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('actualizar_movimiento/<int:row_index>/', views.actualizar_movimiento, name='actualizar_movimiento'),
    path('eliminar_movimiento/<int:row_index>/', views.eliminar_movimiento, name='eliminar_movimiento'),
    path('mostrar_movimientos/', views.mostrar_movimientos, name='mostrar_movimientos'),
]