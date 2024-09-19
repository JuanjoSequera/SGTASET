from django.urls import path
from .import views

urlpatterns = [
    path("materiales/", views.material_crud, name="materiales"),
    path("materiales/agregar/", views.agregar, name="material_agregar"),
    path("materiales/borrar/", views.borrar_materiales, name="borrar_materiales"),
    path("materiales/importar-csv/", views.importar_csv, name="importar_csv"),
    
   
]

