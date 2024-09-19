from django.urls import path
from . import views

urlpatterns = [
path('material_x_deposito/', views.material_x_deposito_crud, name='material_x_deposito'),
path('registrar_material_x_deposito/', views.registrar_material_x_deposito, name='registrar_material_x_deposito'),
path('edicionMaterial_x_deposito/<int:ID_MXD>/', views.edicionMaterial_x_deposito, name='edicionMaterial_x_deposito'),
path('material_x_deposito/guardar_edicion_material_x_deposito/<int:ID_MXD>/', views.guardar_edicion_material_x_deposito, name='guardar_edicion_material_x_deposito'),
path('eliminar_material_x_deposito/<int:ID_MXD>/', views.eliminar_material_x_deposito, name='eliminar_material_x_deposito'),
path('generar_pdf/', views.generar_pdf, name='generar_pdf'),
path('generar_ficha_pdf/<int:material_x_deposito_id>/', views.generar_ficha_pdf, name='generar_ficha_pdf'),
]
