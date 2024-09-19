from django.urls import path
from .import views

urlpatterns = [
    path("tarea/", views.tarea_crud, name="tarea"),
    path('registrarTarea/', views.registrarTarea),
    path('edicionTarea/<ID_Tarea>', views.edicionTarea),
    path('tarea/editarTarea/<int:ID_Tarea>/', views.editarTarea, name='editarTarea'),
    path('eliminarTarea/<ID_Tarea>', views.eliminarTarea)
]