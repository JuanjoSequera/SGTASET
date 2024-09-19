from django.shortcuts import render, redirect
from .models import Transferencias
from .forms import TransferenciaForm
from material_x_deposito.models import Material_x_Deposito
from empleado.models import Empleado
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def transferencias(request):
    transferenciasListadas = Transferencias.objects.all()
    materiales_x_depositos = Material_x_Deposito.objects.all().order_by(
        'ID_Material__nombre_material')
    empleados = Empleado.objects.all().order_by('Nombre', 'Apellido')

    # Obtener el valor del parámetro de búsqueda
    search_query = request.GET.get('q', '')

    # Filtrar las transferencias por nombre de material, nombre de depósito origen o destino que contenga el valor de búsqueda
    if search_query:
        transferenciasListadas = transferenciasListadas.filter(
            Q(ID_MXD_Origen__ID_Material__nombre_material__icontains=search_query) |
            Q(ID_MXD_Destino__ID_Material__nombre_material__icontains=search_query) |
            Q(ID_MXD_Origen__ID_Deposito__nombre_deposito__icontains=search_query) |
            Q(ID_MXD_Destino__ID_Deposito__nombre_deposito__icontains=search_query)
        )

    # Número de transferencias que deseas mostrar por página
    elementos_por_pagina = 10

    # Crear un objeto Paginator
    paginator = Paginator(transferenciasListadas, elementos_por_pagina)

    # Obtener el número de página actual desde la URL
    pagina = request.GET.get('page')

    try:
        # Obtener la página actual
        transferencias = paginator.get_page(pagina)
    except PageNotAnInteger:
        # Si la página no es un número entero, mostrar la primera página
        transferencias = paginator.get_page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        transferencias = paginator.get_page(paginator.num_pages)

    return render(request, 'transferencias.html', {'transferencias': transferencias, 'materiales_x_depositos': materiales_x_depositos, 'empleados': empleados})


def registrarTransferencia(request):
    material_deposito_id_origen = request.POST['ddlMaterialDepositoOrigen']
    material_deposito_id_destino = request.POST['ddlMaterialDepositoDestino']
    empleado_id = request.POST['ddlEmpleado']
    cantidad = int(request.POST['txtCantidad'])  # Convertir a entero

    material_deposito_origen = Material_x_Deposito.objects.get(
        ID_MXD=material_deposito_id_origen)
    material_deposito_destino = Material_x_Deposito.objects.get(
        ID_MXD=material_deposito_id_destino)
    empleado = Empleado.objects.get(ID_Empleado=empleado_id)

    if material_deposito_origen == material_deposito_destino:
        # Si es el mismo depósito, mostrar mensaje de error y redirigir a la página de transferencias
        messages.error(
            request, "No se puede realizar la transferencia. Los depósitos de origen y destino son iguales.")
        return redirect('transferencias')

    if material_deposito_origen.ID_Material != material_deposito_destino.ID_Material:
        # Si los materiales son diferentes, mostrar mensaje de error y redirigir a la página de transferencias
        messages.error(
            request, "No se puede realizar la transferencia. Los materiales no son iguales.")
        return redirect('transferencias')

    errors_or_warnings = False

    with transaction.atomic():  # Usamos una transacción para asegurar la consistencia de la base de datos
        # Verificar si hay suficiente stock en el depósito de origen para realizar la transferencia
        if material_deposito_origen.Cantidad >= cantidad:
            # Actualizamos las cantidades en los depósitos origen y destino
            material_deposito_origen.Cantidad -= cantidad
            material_deposito_origen.save()

            material_deposito_destino.Cantidad += cantidad
            material_deposito_destino.save()

        else:
            # Si no hay suficiente stock en el depósito de origen, mostrar mensaje de error y redirigir a la página de transferencias
            messages.error(
                request, "No hay suficiente stock en el depósito de origen para realizar la transferencia.")
            errors_or_warnings = True
            return redirect('transferencias')

        # Verificar si la cantidad en el depósito de destino después de la transferencia supera el stock máximo
        if material_deposito_destino.Cantidad > material_deposito_destino.Stock_max:
            messages.warning(
                request, "La cantidad en el depósito de destino después de la transferencia supera el stock máximo.")
            errors_or_warnings = True

        # Verificar si la cantidad en el depósito de destino después de la transferencia es menor que el stock mínimo
        if material_deposito_destino.Cantidad < material_deposito_destino.Stock_min:
            messages.warning(
                request, "La cantidad en el depósito de destino después de la transferencia es menor que el stock mínimo.")
            errors_or_warnings = True

        # Verificar si la cantidad en el depósito de origen después de la transferencia supera el stock máximo
        if material_deposito_origen.Cantidad > material_deposito_origen.Stock_max:
            messages.warning(
                request, "La cantidad en el depósito de origen después de la transferencia supera el stock máximo.")
            errors_or_warnings = True

        # Verificar si la cantidad en el depósito de origen después de la transferencia es menor que el stock mínimo
        if material_deposito_origen.Cantidad < material_deposito_origen.Stock_min:
            messages.warning(
                request, "La cantidad en el depósito de origen después de la transferencia es menor que el stock mínimo.")
            errors_or_warnings = True

        # Crear el registro de la transferencia
        transferencia = Transferencias.objects.create(
            ID_MXD_Origen=material_deposito_origen, ID_MXD_Destino=material_deposito_destino, ID_Empleado=empleado, Cantidad=cantidad)

        if not errors_or_warnings:
            # Mostrar mensaje de éxito si no hubo errores ni advertencias
            messages.success(
                request, "La transferencia se ha realizado exitosamente.")

    return redirect('transferencias')


def edicionTransferencia(request, ID_Transferencias):
    transferencia = Transferencias.objects.get(
        ID_Transferencias=ID_Transferencias)
    materiales_x_depositos = Material_x_Deposito.objects.all()
    empleados = Empleado.objects.all()
    form = TransferenciaForm(instance=transferencia)
    return render(request, 'edicion_transferencia.html', {'form': form, 'transferencia': transferencia, 'materiales_x_depositos': materiales_x_depositos, 'empleados': empleados})


def editarTransferencia(request, ID_Transferencias):
    Transferencias = Transferencias.objects.get(ID_Transferencias=ID_Transferencias)

    if request.method == 'POST':
        T_MxD_origen_nuevo = request.POST['ddlMaterialDepositoOrigen']
        T_MxD_destino_nuevo = request.POST['ddlMaterialDepositoDestino']
        empleado_id = request.POST['ddlEmpleado']
        T_cantidad_nuevo = request.POST['txtCantidad']

        T_MxD_origen_anterior = Transferencias.ID_MXD_Origen
        T_MxD_destino_anterior = Transferencias.ID_MXD_Destino
        T_cantidad_anterior = Transferencias.Cantidad

        MxD_origen_nuevo = Material_x_Deposito.objects.get(ID_MXD=T_MxD_origen_nuevo)
        MxD_destino_nuevo = Material_x_Deposito.objects.get(ID_MXD=T_MxD_destino_nuevo)
        empleado = Empleado.objects.get(ID_Empleado=empleado_id)\
        
        MxD_origen_anterior = Material_x_Deposito.objects.get(ID_MXD=T_MxD_origen_anterior)
        MxD_destino_anterior = Material_x_Deposito.objects.get(ID_MXD=T_MxD_destino_anterior)

        errors = False
        warning = False

        if T_MxD_origen_nuevo != T_MxD_origen_anterior or T_MxD_destino_nuevo != T_MxD_destino_anterior or T_cantidad_nuevo != T_cantidad_anterior:
            if MxD_origen_nuevo.ID_Material != MxD_destino_nuevo.ID_Material :
                messages.error(
                request, "No hay suficiente stock en el depósito, solicite la compra de materiales para el depósito.")
                errors = True
                return redirect('movimientos')
            
            if T_cantidad_nuevo >= MxD_origen_nuevo: 
                messages.error(
                request, "No hay suficiente stock en el depósito, solicite la compra de materiales para el depósito.")
                errors = True
                return redirect('movimientos')
            
        if not errors:
            transferencia = Transferencias.objects.get(ID_Transferencias=ID_Transferencias)
            transferencia.ID_MXD_origen = T_MxD_origen_nuevo
            transferencia.ID_MXD_destino = T_MxD_destino_nuevo
            transferencia.ID_Empleado = empleado
            transferencia.Cantidad = T_cantidad_nuevo

            transferencia.save()

            if not warning:
                messages.success(request, 'Transferencia editada correctamente')

        return redirect('transferencias')


def eliminarTransferencia(request, ID_Transferencias):
    # Obtener la transferencia a eliminar
    transferencia = Transferencias.objects.get(
        ID_Transferencias=ID_Transferencias)

    # Obtener los depósitos de origen y destino de la transferencia
    material_deposito_origen = transferencia.ID_MXD_Origen
    material_deposito_destino = transferencia.ID_MXD_Destino

    # Tomar el valor absoluto de la cantidad transferida
    cantidad = abs(transferencia.Cantidad)

    with transaction.atomic():  # Usamos una transacción para asegurar la consistencia de la base de datos
        # Verificar si hay suficiente stock en el depósito de destino para restaurar la transferencia
        if material_deposito_destino.Cantidad >= cantidad:
            # Restauramos las cantidades en los depósitos origen y destino
            material_deposito_origen.Cantidad += cantidad
            material_deposito_destino.Cantidad -= cantidad

            material_deposito_origen.save()
            material_deposito_destino.save()
        else:
            # Si no hay suficiente stock en el depósito de destino, mostrar mensaje de error y redirigir a la página de transferencias
            messages.error(
                request, "No hay suficiente stock en el depósito de destino para eliminar la transferencia.")
            return redirect('transferencias')

        # Verificar si la cantidad en el depósito de origen después de restaurar la transferencia supera el stock máximo
        if material_deposito_origen.Cantidad > material_deposito_origen.Stock_max:
            messages.warning(
                request, "La cantidad en el depósito de origen después de eliminar la transferencia supera el stock máximo.")

        # Verificar si la cantidad en el depósito de origen después de restaurar la transferencia es menor que el stock mínimo
        if material_deposito_origen.Cantidad < material_deposito_origen.Stock_min:
            messages.warning(
                request, "La cantidad en el depósito de origen después de eliminar la transferencia es menor que el stock mínimo.")

        # Verificar si la cantidad en el depósito de destino después de restaurar la transferencia supera el stock máximo
        if material_deposito_destino.Cantidad > material_deposito_destino.Stock_max:
            messages.warning(
                request, "La cantidad en el depósito de destino después de eliminar la transferencia supera el stock máximo.")

        # Verificar si la cantidad en el depósito de destino después de restaurar la transferencia es menor que el stock mínimo
        if material_deposito_destino.Cantidad < material_deposito_destino.Stock_min:
            messages.warning(
                request, "La cantidad en el depósito de destino después de eliminar la transferencia es menor que el stock mínimo.")

        # Eliminar la transferencia
        transferencia.delete()

    messages.success(request, 'Transferencia eliminada correctamente')
    return redirect('transferencias')
