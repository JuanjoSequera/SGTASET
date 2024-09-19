from django.shortcuts import render, redirect
from .models import Empleado
from orden_de_trabajo.models import Orden_de_trabajo
from movimiento.models import Movimiento
from transferencia.models import Transferencias
from deposito.models import Deposito
from django.contrib import messages
from cargo.models import Cargo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cargo.models import Cargo
from django.db.models import Q

def empleado_crud(request): 
    if request.user.is_authenticated:
        # Obtener todos los empleados
        empleadosListados = Empleado.objects.all()
        cargos = Cargo.objects.all()
        # Obtener el valor del parámetro de búsqueda
        search_query = request.GET.get('q', '')
        # Filtrar los empleados por nombre que contenga el valor de búsqueda
        if search_query:
            empleadosListados = empleadosListados.filter(Nombre__icontains=search_query)
        # Número de empleados que deseas mostrar por página
        elementos_por_pagina = 10
        # Crear un objeto Paginator
        paginator = Paginator(empleadosListados, elementos_por_pagina)
        # Obtener el número de página actual desde la URL
        pagina = request.GET.get('page')
        try:
            # Obtener la página actual
            empleados = paginator.get_page(pagina)
        except PageNotAnInteger:
            # Si la página no es un número entero, mostrar la primera página
            empleados = paginator.get_page(1)
        except EmptyPage:
            # Si la página está fuera de rango, mostrar la última página
            empleados = paginator.get_page(paginator.num_pages)

        return render(request, "empleado.html", {"empleados": empleados,  "cargos": cargos})
    else:
        return redirect('login')

def registrarEmpleado(request):
    nombre = request.POST['txtNombre']
    apellido = request.POST['txtApellido']
    ci = request.POST['txtCI']
    telefono = request.POST['txtTelefono']
    direccion = request.POST['txtDireccion']
    mail = request.POST['txtMail']
    salario = request.POST['txtSalario']
    cargo_id = request.POST['ddlCargo']

    cargo = Cargo.objects.get(id_cargo=cargo_id)

    empleado = Empleado.objects.create(Nombre=nombre, Apellido=apellido, CI=ci, Telefono=telefono, Direccion=direccion, Mail=mail, Salario=salario, ID_Cargo=cargo)

    messages.success(request, 'Empleado registrado correctamente')

    return redirect('empleado')

def edicionEmpleado(request, ID_Empleado):
    empleado = Empleado.objects.get(ID_Empleado=ID_Empleado)
    cargos = Cargo.objects.all()
    return render(request, "edicionEmpleado.html", {"empleado": empleado, "cargos": cargos})

def editarEmpleado(request, ID_Empleado):
    nombre = request.POST['txtNombre']
    apellido = request.POST['txtApellido']
    ci = request.POST['txtCI']
    telefono = request.POST['txtTelefono']
    direccion = request.POST['txtDireccion']
    mail = request.POST['txtMail']
    salario = request.POST['txtSalario']
    cargo_id = request.POST['ddlCargo']

    cargo = Cargo.objects.get(id_cargo=cargo_id)

    empleado = Empleado.objects.get(ID_Empleado=ID_Empleado)
    empleado.Nombre = nombre
    empleado.Apellido = apellido
    empleado.CI = ci
    empleado.Telefono = telefono
    empleado.Direccion = direccion
    empleado.Mail = mail
    empleado.Salario = salario
    empleado.ID_Cargo = cargo
    empleado.save()

    messages.success(request, 'Empleado editado correctamente')

    return redirect('empleado')

def eliminarEmpleado(request, ID_Empleado):
    try:
        empleado = Empleado.objects.get(ID_Empleado=ID_Empleado)

        # Verificar si el empleado está relacionado con alguna Orden_de_trabajo
        if Orden_de_trabajo.objects.filter(
                Q(ID_Empleado_tecnico=empleado) | Q(ID_Empleado_ayudante=empleado)
        ).exists():
            messages.error(request, 'No se puede eliminar el empleado porque está relacionado con una Orden de Trabajo.')
        # Verificar si el empleado está relacionado con algún Movimiento
        elif Movimiento.objects.filter(ID_Empleado=empleado).exists():
            messages.error(request, 'No se puede eliminar el empleado porque está relacionado con un Movimiento.')
        # Verificar si el empleado está relacionado con alguna Transferencia
        elif Transferencias.objects.filter(ID_Empleado=empleado).exists():
            messages.error(request, 'No se puede eliminar el empleado porque está relacionado con una Transferencia.')
        # Verificar si el empleado está relacionado con algún Depósito
        elif Deposito.objects.filter(ID_Empleado=empleado).exists():
            messages.error(request, 'No se puede eliminar el empleado porque está relacionado con un Depósito.')
        else:
            empleado.delete()
            messages.success(request, 'Empleado eliminado correctamente')
    except Empleado.DoesNotExist:
        messages.error(request, 'Empleado no encontrado.')

    return redirect('empleado')
