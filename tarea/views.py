from django.shortcuts import render,redirect
from .models import  Tarea
from orden_de_trabajo.models import Orden_de_trabajo
from django.contrib import messages
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def tarea_crud(request):
    if request.user.is_authenticated:
        # Obtener todas las tareas
        tareasListadas = Tarea.objects.all()

        # Obtener el valor del parámetro de búsqueda
        search_query = request.GET.get('q', '')

        # Filtrar las tareas por nombre que contenga el valor de búsqueda
        if search_query:
            tareasListadas = tareasListadas.filter(Nombre__icontains=search_query)

        # Número de tareas que deseas mostrar por página
        elementos_por_pagina = 10

        # Crear un objeto Paginator
        paginator = Paginator(tareasListadas, elementos_por_pagina)

        # Obtener el número de página actual desde la URL
        pagina = request.GET.get('page')

        try:
            # Obtener la página actual
            tareas_pagina = paginator.get_page(pagina)
        except PageNotAnInteger:
            # Si la página no es un número entero, mostrar la primera página
            tareas_pagina = paginator.get_page(1)
        except EmptyPage:
            # Si la página está fuera de rango, mostrar la última página
            tareas_pagina = paginator.get_page(paginator.num_pages)

        return render(request, "tarea.html", {"tareas_pagina": tareas_pagina})
    else:
        return redirect('login')


def registrarTarea(request):
    if request.method == 'POST':
        nombre = request.POST['txtTarea']
        
        nombre = Tarea.objects.create(Nombre=nombre)

        messages.success(request, 'Tarea cargada correctamente')

        return redirect('tarea')

def edicionTarea(request, ID_Tarea):
    tarea = Tarea.objects.get(ID_Tarea=ID_Tarea)
    return render(request, "edicionTarea.html", {"tarea":tarea})

def editarTarea(request, ID_Tarea):
    if request.method == 'POST':
        nombre = request.POST.get('txtTarea', '')
        tarea = Tarea.objects.get(ID_Tarea=ID_Tarea)
        tarea.Nombre = nombre
        tarea.save()
        messages.success(request, 'Tarea editada correctamente')
    return redirect('tarea')


def eliminarTarea(request, ID_Tarea):
    try:
        tarea = Tarea.objects.get(ID_Tarea=ID_Tarea)
        # Verificar si la tarea está asignada a alguna Orden_de_trabajo
        if Orden_de_trabajo.objects.filter(ID_Tarea=tarea).exists():
            messages.error(request, 'No se puede eliminar la tarea porque está asignada a una Orden de Trabajo.')
        else:
            tarea.delete()
            messages.success(request, 'Tarea eliminada correctamente')
    except Tarea.DoesNotExist:
        messages.error(request, 'Tarea no encontrada.')

    return redirect('tarea')


