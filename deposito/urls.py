from django.urls import path
from .import views

urlpatterns = [
    path("deposito/", views.deposito_crud, name="depositos"),
    path('registrarDeposito/', views.registrarDeposito),
    path('edicionDeposito/<int:id_deposito>/', views.edicionDeposito, name="edicionDeposito"),
    path('editarDeposito/<int:id_deposito>/', views.editarDeposito, name="editarDeposito"),
    path('eliminarDeposito/<int:id_deposito>/', views.eliminarDeposito, name="eliminarDeposito"),
]
