from django.shortcuts import render,redirect
from .models import  Cargo
from django.core.paginator import Paginator
from .forms import CargoForm
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Cargo
from empleado.models import Empleado
from django.contrib import messages

def cargo_crud(request): 
    if request.user.is_authenticated:
        # Obtener todos los cargos
        listaCargo = Cargo.objects.all()

        # Obtener el valor del parámetro de búsqueda
        search_query = request.GET.get('q', '')

        # Filtrar los cargos por nombre que contenga el valor de búsqueda
        if search_query:
            listaCargo = listaCargo.filter(nombre_cargo__icontains=search_query)

        # Número de cargos que deseas mostrar por página
        elementos_por_pagina = 10

        # Crear un objeto Paginator
        paginator = Paginator(listaCargo, elementos_por_pagina)

        # Obtener el número de página actual desde la URL
        pagina = request.GET.get('page')

        try:
            # Obtener la página actual
            cargos_pagina = paginator.get_page(pagina)
        except PageNotAnInteger:
            # Si la página no es un número entero, mostrar la primera página
            cargos_pagina = paginator.get_page(1)
        except EmptyPage:
            # Si la página está fuera de rango, mostrar la última página
            cargos_pagina = paginator.get_page(paginator.num_pages)

        return render(request, "cargo/cargo.html", {"cargos_pagina": cargos_pagina})
    else:
        return redirect('login')
    
def registrarCargo(request):
    if request.method == 'POST':
        nombre = request.POST['txtCargo']
        nombre = Cargo.objects.create(nombre_cargo=nombre)
        messages.success(request, 'Cargo registrado correctamente')
        return redirect('cargo')

def edicionCargo(request, id_cargo):
    cargo= Cargo.objects.get(id_cargo=id_cargo)
    return render(request, "cargo/editar.html", {"cargo":cargo})

def editarCargo(request, id_cargo):
    nombre = request.POST['txtCargo']
    cargo = Cargo.objects.get(id_cargo=id_cargo)
    cargo.nombre_cargo = nombre
    cargo.save()
    messages.success(request, 'Cargo editado correctamente')
    return redirect('cargo')


def eliminarCargo(request, id_cargo):
    try:
        cargo = Cargo.objects.get(id_cargo=id_cargo)

        # Verificar si existen empleados que tengan asignado el cargo
        if Empleado.objects.filter(ID_Cargo=cargo).exists():
            messages.error(request, 'No se puede eliminar el cargo porque está asignado a empleados.')
        else:
            cargo.delete()
            messages.success(request, 'Cargo eliminado correctamente')
    except Cargo.DoesNotExist:
        messages.error(request, 'Cargo no encontrado.')

    return redirect('cargo')


