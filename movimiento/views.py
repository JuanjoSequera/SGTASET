from django.shortcuts import render, redirect
from .models import Movimiento
from material_x_deposito.models import Material_x_Deposito
from empleado.models import Empleado
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def movimientos(request):
    movimientosListados = Movimiento.objects.all()
    materiales_x_depositos = Material_x_Deposito.objects.all().order_by(
        'ID_Material__nombre_material')
    empleados = Empleado.objects.all().order_by('Nombre', 'Apellido')
    # Obtener el valor del parámetro de búsqueda
    search_query = request.GET.get('q', '')
    # Filtrar los movimientos por concepto que contenga el valor de búsqueda
    if search_query:
        movimientosListados = movimientosListados.filter(
            Concepto__icontains=search_query)
    # Número de movimientos que deseas mostrar por página
    elementos_por_pagina = 10
    # Crear un objeto Paginator
    paginator = Paginator(movimientosListados, elementos_por_pagina)
    # Obtener el número de página actual desde la URL
    pagina = request.GET.get('page')
    try:
        # Obtener la página actual
        movimientos = paginator.get_page(pagina)
    except PageNotAnInteger:
        # Si la página no es un número entero, mostrar la primera página
        movimientos = paginator.get_page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        movimientos = paginator.get_page(paginator.num_pages)

    return render(request, 'movimientos.html', {'movimientos': movimientos, 'materiales_x_depositos': materiales_x_depositos, 'empleados': empleados, 'search_query': search_query})


def registrarMovimiento(request):
    material_deposito_id = request.POST['ddlMaterialDeposito']
    empleado_id = request.POST['ddlEmpleado']
    concepto = request.POST['txtConcepto']
    cantidad = int(request.POST['txtCantidad'])  # Convertir a entero
    signo = int(request.POST['ddlSigno'])  # Convertir a entero

    material_deposito = Material_x_Deposito.objects.get(
        ID_MXD=material_deposito_id)
    empleado = Empleado.objects.get(ID_Empleado=empleado_id)

    errors_or_warnings = False

    with transaction.atomic():
        # Asegurarse de que la cantidad sea siempre positiva tanto para movimientos de entrada como de salida
        cantidad_registrada = abs(cantidad)

        if signo == -1:  # Si es un movimiento de salida, verificar el stock suficiente
            if material_deposito.Cantidad >= cantidad_registrada:
                material_deposito.Cantidad -= cantidad_registrada
            else:
                messages.error(
                    request, "No hay suficiente stock en el depósito, solicite la compra de materiales para el depósito, no se ha registrado el movimiento.")
                errors_or_warnings = True
                return redirect('movimientos')

            if material_deposito.Cantidad < material_deposito.Stock_min:
                messages.warning(
                    request, "La cantidad después del movimiento será menor al stock mínimo.")
                errors_or_warnings = True

        else:  # Si es un movimiento de entrada, simplemente sumar la cantidad
            material_deposito.Cantidad += cantidad_registrada

            if material_deposito.Cantidad > material_deposito.Stock_max:
                messages.warning(
                    request, "La cantidad después del movimiento será mayor al stock máximo.")
                errors_or_warnings = True

        if not errors_or_warnings:
            messages.success(
                request, "El movimiento se ha realizado exitosamente.")
            errors_or_warnings = True

        material_deposito.save()

        # Usar una cantidad positiva en la base de datos, pero almacenar el signo por separado para mostrarlo según el tipo de movimiento al registrar
        movimiento = Movimiento.objects.create(
            ID_MXD=material_deposito, ID_Empleado=empleado, Concepto=concepto, Cantidad=cantidad_registrada, Signo=signo)

    return redirect('movimientos')


def edicionMovimiento(request, movimiento_id):
    movimiento = Movimiento.objects.get(ID_Movimiento=movimiento_id)
    # O los filtros que necesites para los materiales por depósito
    materiales_deposito = Material_x_Deposito.objects.all()
    # O los filtros que necesites para los empleados
    empleados = Empleado.objects.all()

    return render(request, 'edicionMovimiento.html', {'movimiento': movimiento, 'materiales_deposito': materiales_deposito, 'empleados': empleados})


def editarMovimiento(request, ID_Movimiento):
    movimiento = Movimiento.objects.get(ID_Movimiento=ID_Movimiento)

    if request.method == 'POST':
        MxD_nuevo = request.POST['ddlMaterialDeposito']
        empleado_id = request.POST['ddlEmpleado']
        concepto = request.POST['txtConcepto']
        cantidad_nueva = int(request.POST['txtCantidad'])  # Convertir a entero
        signo_nuevo = int(request.POST['ddlSigno'])  # Convertir a entero


        MxD_anterior = movimiento.ID_MXD
        cantidad_anterior = movimiento.Cantidad
        signo_anterior = movimiento.Signo

        material_deposito = Material_x_Deposito.objects.get(ID_MXD=MxD_nuevo)
        empleado = Empleado.objects.get(ID_Empleado=empleado_id)

        errors = False
        warning = False

            # Verificar si se cambió el tipo de movimiento o la cantidad
        if movimiento.Signo != signo_nuevo or cantidad_anterior != cantidad_nueva or movimiento.ID_MXD != MxD_nuevo or movimiento.ID_Empleado != empleado_id or movimiento.Concepto != concepto:
            if signo_nuevo == -1:  # Si es un movimiento de salida, verificar el stock suficiente
                if material_deposito.Cantidad + cantidad_anterior < cantidad_nueva:
                    messages.error(
                        request, "No hay suficiente stock en el depósito, solicite la compra de materiales para el depósito.")
                    errors = True
                    return redirect('movimientos')

                if material_deposito.Cantidad - cantidad_anterior + cantidad_nueva < material_deposito.Stock_min:
                    messages.warning(
                        request, "La cantidad después del movimiento será menor al stock mínimo.")
                    warning = True

                if material_deposito.Cantidad + cantidad_anterior - cantidad_nueva < 0:
                    messages.error(
                        request, "La cantidad después del movimiento será negativa en el depósito.")
                    errors = True
                    return redirect('movimientos')
                
                if signo_nuevo != signo_anterior:
                    if material_deposito.Cantidad - (cantidad_anterior + cantidad_nueva) < 0:
                        messages.error(
                            request, "La cantidad resultante en el depósito será negativa.")
                        errors = True
                        return redirect('movimientos')

            else:  # Si es un movimiento de entrada, verificar el stock máximo
                if material_deposito.Cantidad - cantidad_anterior + cantidad_nueva > material_deposito.Stock_max:
                    messages.warning(
                        request, "La cantidad después del movimiento será mayor al stock máximo.")
                    warning = True

        if not errors:

            if signo_anterior == -1:
                MxD_anterior.Cantidad += cantidad_anterior
            else:
                MxD_anterior.Cantidad -= cantidad_anterior

            MxD_anterior.save()

            # Eliminar el movimiento anterior
            movimiento.delete()

            # Obtener la instancia de Material_x_Deposito correspondiente a MxD_nuevo
            MxD_nuevo_instancia = Material_x_Deposito.objects.get(ID_MXD=MxD_nuevo)

            # Crear un nuevo movimiento con los valores editados
            nuevo_movimiento = Movimiento(
                ID_MXD=MxD_nuevo_instancia,
                ID_Empleado=empleado,
                Concepto=concepto,
                Cantidad=cantidad_nueva,
                Signo=signo_nuevo
            )
            nuevo_movimiento.save()

            if signo_nuevo == -1:
                MxD_nuevo_instancia.Cantidad -= cantidad_nueva
            else:
                MxD_nuevo_instancia.Cantidad += cantidad_nueva

            MxD_nuevo_instancia.save()

            if not warning:
                messages.success(request, "El movimiento se ha editado exitosamente.")
            return redirect('movimientos')


        # Si no se realizaron cambios, simplemente redirigir a la página de movimientos
        return redirect('movimientos')

    # Cargar los datos del movimiento en el formulario de edición
    materiales_x_depositos = Material_x_Deposito.objects.all()
    empleados = Empleado.objects.all()

    return render(request, 'editar_movimiento.html', {
        'movimiento': movimiento,
        'materiales_x_depositos': materiales_x_depositos,
        'empleados': empleados
    })


def eliminarMovimiento(request, ID_Movimiento):
    movimiento = Movimiento.objects.get(ID_Movimiento=ID_Movimiento)
    signo = movimiento.Signo
    cantidad = abs(movimiento.Cantidad)

    with transaction.atomic():
        # Obtener el material por depósito asociado al movimiento
        material_deposito = movimiento.ID_MXD

        if signo == -1:  # Si es un movimiento de salida, sumar la cantidad al material_x_deposito
            material_deposito.Cantidad += cantidad
        else:  # Si es un movimiento de entrada, verificar si hay suficiente cantidad antes de eliminar
            if material_deposito.Cantidad < cantidad:
                messages.error(
                    request, "No se puede eliminar el movimiento. No hay suficiente cantidad en el depósito.")
                return redirect('movimientos')

            material_deposito.Cantidad -= cantidad

            # Verificar si la cantidad después de restaurar el movimiento es menor al stock mínimo
            if material_deposito.Cantidad < material_deposito.Stock_min:
                messages.warning(
                    request, "La cantidad después de eliminar el movimiento es menor al stock mínimo.")

        # Verificar si la cantidad después de restaurar el movimiento supera el stock máximo
        if material_deposito.Cantidad > material_deposito.Stock_max:
            messages.warning(
                request, "La cantidad después de eliminar el movimiento supera el stock máximo.")

        # Guardar el objeto material_x_deposito actualizado
        material_deposito.save()

        # Eliminar el movimiento
        movimiento.delete()

    messages.success(request, 'Movimiento eliminado correctamente')
    return redirect('movimientos')
