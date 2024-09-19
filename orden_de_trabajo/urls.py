from django.urls import path
from .import views

urlpatterns = [
    path("orden_de_trabajo/", views.orden_de_trabajo_crud, name="orden"),
    path('edicionOrden/<nro_orden>', views.edicionOrden,name='asignar_empleados_movil'),
    path('editarOrden/<nro_orden>', views.editarOrden,name='asignar_empleados_moviles'), 
    path("orden/importar_csv_orden/", views.importar_csv_orden,name='importar_csv_orden'),
    path('generar_pdf/<int:nro_orden>/', views.generar_pdf_orden, name='generar_pdf_orden'),
    path("ot_en_progreso/", views.ot_en_progreso_crud, name="orden_progreso"),
    path('terminarOT/<nro_orden>', views.terminarOrden,name='terminar_orden'),
    path('dardebajaot/<nro_orden>', views.dardebajaOrden,name='dar_de_baja_ot'),
    path("ot_terminada/", views.ot_terminada_crud, name="orden_terminada"), 
    path("ot_rechazada/", views.ot_rechazado_crud, name="orden_rechazada"), 
    ]