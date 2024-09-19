from django.urls import path
from .import views

urlpatterns = [
    path("empleado/", views.empleado_crud, name="empleado"),
    path('registrarEmpleado/', views.registrarEmpleado),
    path('edicionEmpleado/<ID_Empleado>', views.edicionEmpleado),
    path('editarEmpleado/<ID_Empleado>', views.editarEmpleado),
    path('eliminarEmpleado/<ID_Empleado>', views.eliminarEmpleado)
]
