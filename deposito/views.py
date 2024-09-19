from django.shortcuts import render, redirect
from .models import Deposito
from material.models import Material
from material_x_deposito.models import Material_x_Deposito
from movimiento.models import Movimiento
from transferencia.models import Transferencias
from orden_de_trabajo.models import Orden_de_trabajo
from django.contrib import messages
from empleado.models import Empleado
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def deposito_crud(request): 
    if request.user.is_authenticated:
        # Obtener todos los depósitos
        depositosListados = Deposito.objects.all()

        # Obtener el valor del parámetro de búsqueda
        search_query = request.GET.get('q', '')

        # Filtrar los depósitos por nombre de depósito que contenga el valor de búsqueda
        if search_query:
            depositosListados = depositosListados.filter(nombre_deposito__icontains=search_query)

        # Número de depósitos que deseas mostrar por página
        elementos_por_pagina = 10

        # Crear un objeto Paginator
        paginator = Paginator(depositosListados, elementos_por_pagina)

        # Obtener el número de página actual desde la URL
        pagina = request.GET.get('page')

        try:
            # Obtener la página actual
            depositos = paginator.get_page(pagina)
        except PageNotAnInteger:
            # Si la página no es un número entero, mostrar la primera página
            depositos = paginator.get_page(1)
        except EmptyPage:
            # Si la página está fuera de rango, mostrar la última página
            depositos = paginator.get_page(paginator.num_pages)

        empleados = Empleado.objects.all()  # Obtener todos los empleados

        return render(request, "deposito.html", {"depositos": depositos, "empleados": empleados})

    else:
        return redirect('login')



def registrarDeposito(request):
    if request.method == 'POST':
        id_empleado = request.POST['ddlEmpleado']
        nombre_deposito = request.POST['txtNombreDeposito']
        tipo_deposito = request.POST['ddlTipoDeposito']

        empleado = Empleado.objects.get(ID_Empleado=id_empleado)
        deposito = Deposito.objects.create(ID_Empleado=empleado, nombre_deposito=nombre_deposito, tipo_deposito=tipo_deposito)

        # Crear Material_x_Deposito para cada material existente
        materiales = Material.objects.all()

        for material in materiales:
            material_por_deposito_existente = Material_x_Deposito.objects.filter(ID_Material=material, ID_Deposito=deposito).exists()
            if not material_por_deposito_existente:
                Material_x_Deposito.objects.create(
                    ID_Material=material,
                    ID_Deposito=deposito,
                    Cantidad=0,
                    Stock_min=10,
                    Stock_max=20,
                    Unidad_medida="cantidad"
                )

        messages.success(request, 'Depósito cargado correctamente')

        return redirect('depositos')



def edicionDeposito(request, id_deposito):
    deposito = Deposito.objects.get(id_deposito=id_deposito)
    empleado = Empleado.objects.all()
    return render(request, "editar.html", {"depositos": deposito, "empleados": empleado})

def editarDeposito(request, id_deposito):
    id_empleado = request.POST['ddlEmpleado']
    nombre_deposito = request.POST['txtNombreDeposito']
    tipo_deposito = request.POST['ddlTipoDeposito']

    empleado = Empleado.objects.get(ID_Empleado=id_empleado)
    deposito = Deposito.objects.get(id_deposito=id_deposito)

    deposito.ID_Empleado = empleado
    deposito.nombre_deposito = nombre_deposito
    deposito.tipo_deposito = tipo_deposito

    deposito.save()

    messages.success(request, 'Depósito editado correctamente')
    #messages.error(request, 'Hubo un error al editar el depósito')

    return redirect('depositos')


def eliminarDeposito(request, id_deposito):
    try:
        deposito = Deposito.objects.get(id_deposito=id_deposito)

        # Verificar si el depósito está relacionado con alguna Transferencia (Origen o Destino)
        if Transferencias.objects.filter(Q(ID_MXD_Origen__ID_Deposito=deposito) | Q(ID_MXD_Destino__ID_Deposito=deposito)).exists():
            messages.error(request, 'No se puede eliminar el depósito porque está relacionado con una Transferencia.')
        # Verificar si el depósito está relacionado con algún Movimiento
        elif Movimiento.objects.filter(ID_MXD__ID_Deposito=deposito).exists():
            messages.error(request, 'No se puede eliminar el depósito porque está relacionado con un Movimiento.')
        # Verificar si el depósito está relacionado con alguna Orden_de_trabajo
        elif Orden_de_trabajo.objects.filter(id_deposito=deposito).exists():
            messages.error(request, 'No se puede eliminar el depósito porque está relacionado con una Orden de Trabajo.')
        # Verificar si el depósito está relacionado con algún Material_x_Deposito
        elif Material_x_Deposito.objects.filter(ID_Deposito=deposito).exists():
            messages.error(request, 'No se puede eliminar el depósito porque está relacionado con un Material por Depósito.')
        else:
            deposito.delete()
            messages.success(request, 'Depósito eliminado correctamente')
    except Deposito.DoesNotExist:
        messages.error(request, 'Depósito no encontrado.')

    return redirect('depositos')
