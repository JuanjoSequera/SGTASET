from django.urls import path
from .import views


urlpatterns = [
    path("orden_de_trabajo_x_material", views.orden_de_trabajo_material_crud)

]