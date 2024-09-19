from django.urls import path
from . import views

urlpatterns = [
    path('movimientos/', views.movimientos, name='movimientos'),
    path('registrarMovimiento/', views.registrarMovimiento, name='registrarMovimiento'),
    path('edicionMovimiento/<int:movimiento_id>/', views.edicionMovimiento, name='edicionMovimiento'),
    path('editarMovimiento/<int:ID_Movimiento>/', views.editarMovimiento, name='editarMovimiento'),
    path('eliminarMovimiento/<int:ID_Movimiento>/', views.eliminarMovimiento, name='eliminar_movimiento'),
]
