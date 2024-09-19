from django.urls import path
from .import views

urlpatterns =[
    path("cargo/", views.cargo_crud, name="cargo"),
    path('registrarCargo/', views.registrarCargo),
    path('edicionCargo/<id_cargo>', views.edicionCargo),
    path('editarCargo/<id_cargo>', views.editarCargo),
    path('eliminarCargo/<id_cargo>', views.eliminarCargo),
]




