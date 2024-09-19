from django.urls import path
from . import views

urlpatterns = [
    path('transferencias/', views.transferencias, name='transferencias'),
    path('registrarTransferencia/', views.registrarTransferencia, name='registrarTransferencia'),
    path('edicionTransferencia/<int:ID_Transferencias>/', views.edicionTransferencia, name='edicion_transferencia'),
    path('editarTransferencia/<int:ID_Transferencias>/', views.editarTransferencia, name='editarTransferencia'),
    path('eliminarTransferencia/<int:ID_Transferencias>/', views.eliminarTransferencia, name='eliminar_transferencia'),
]
