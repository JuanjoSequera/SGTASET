from django.urls import path
from .import views

urlpatterns = [
    path("clientes/", views.cliente_crud, name="clientes"),
    path("clientes/agregar/", views.agregar, name="clientes_agregar"),
    path("clientes/borrar/", views.borrar_clientes, name="borrar_clientes"),
    path("clientes/importar_csv_cliente/", views.importar_csv_cliente, name="importar_csv_cliente"),
    path('clienttes/actualizar_cliente/',views.actualizar_clientes,name="actualizar_cliente"),
    
    
]
