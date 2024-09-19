from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Material_x_Deposito
from orden_de_trabajo.models import Orden_de_trabajo
from transferencia.models import Transferencias
from movimiento.models import Movimiento
from material.models import Material
from deposito.models import Deposito
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from itertools import chain
from operator import attrgetter
from io import BytesIO


def material_x_deposito_crud(request):
    if request.user.is_authenticated:
        # Obtener todos los materiales por depósito
        materiales_deposito = Material_x_Deposito.objects.all().order_by('ID_Material')

        # Obtener el valor del parámetro de búsqueda
        search_query = request.GET.get('q', '')

        # Filtrar los materiales por depósito que contengan el valor de búsqueda en el nombre del material o depósito
        if search_query:
            materiales_deposito = materiales_deposito.filter(
                # Filtrar por nombre de material
                Q(ID_Material__nombre_material__icontains=search_query) |
                # Filtrar por nombre de depósito
                Q(ID_Deposito__nombre_deposito__icontains=search_query)
            )

        # Número de materiales por depósito que deseas mostrar por página
        elementos_por_pagina = 10

        # Crear un objeto Paginator
        paginator = Paginator(materiales_deposito, elementos_por_pagina)

        # Obtener el número de página actual desde la URL
        pagina = request.GET.get('page')

        try:
            # Obtener la página actual
            materiales_deposito = paginator.get_page(pagina)
        except PageNotAnInteger:
            # Si la página no es un número entero, mostrar la primera página
            materiales_deposito = paginator.get_page(1)
        except EmptyPage:
            # Si la página está fuera de rango, mostrar la última página
            materiales_deposito = paginator.get_page(paginator.num_pages)

        return render(request, "material_x_deposito.html", {"materiales_deposito": materiales_deposito})
    else:
        return redirect('login')


def registrar_material_x_deposito(request):
    if request.method == 'POST':
        id_material = request.POST['ddlMaterial']
        id_deposito = request.POST['ddlDeposito']
        cantidad = request.POST['txtCantidad']
        stock_min = request.POST['txtStockMin']
        stock_max = request.POST['txtStockMax']
        unidad_medida = request.POST['txtUnidadMedida']

        material = Material.objects.get(id_material=id_material)
        deposito = Deposito.objects.get(id_deposito=id_deposito)

        material_x_deposito = Material_x_Deposito.objects.create(
            ID_Material=material, ID_Deposito=deposito, Cantidad=cantidad, Stock_min=stock_min, Stock_max=stock_max, Unidad_medida=unidad_medida)

        return redirect('material_x_deposito')


def edicionMaterial_x_deposito(request, ID_MXD):
    material_x_deposito = Material_x_Deposito.objects.get(ID_MXD=ID_MXD)
    materiales = Material.objects.all()
    depositos = Deposito.objects.all()
    return render(request, "editar_material_x_deposito.html", {"material_x_deposito": material_x_deposito, "materiales": materiales, "depositos": depositos})


def guardar_edicion_material_x_deposito(request, ID_MXD):
    stock_min = request.POST['txtStockMin']
    stock_max = request.POST['txtStockMax']
    unidad_medida = request.POST['txtUnidadMedida']

    material_x_deposito = Material_x_Deposito.objects.get(ID_MXD=ID_MXD)
    material_x_deposito.Stock_min = stock_min
    material_x_deposito.Stock_max = stock_max
    material_x_deposito.Unidad_medida = unidad_medida
    material_x_deposito.save()

    messages.success(request, 'Movimiento eliminado correctamente')

    return redirect('material_x_deposito')


def eliminar_material_x_deposito(request, ID_MXD):
    material_x_deposito = Material_x_Deposito.objects.get(ID_MXD=ID_MXD)
    material_x_deposito.delete()

    return redirect('material_x_deposito')


def generar_pdf(request):
    # Obtener el valor del parámetro de búsqueda
    search_query = request.GET.get('q', '')

    # Obtener la lista de materiales por depósito desde la base de datos
    materiales = Material_x_Deposito.objects.all()

    # Filtrar los materiales por depósito que contengan el valor de búsqueda en el nombre del material o depósito
    if search_query:
        materiales = materiales.filter(
            # Filtrar por nombre de material
            Q(ID_Material__nombre_material__icontains=search_query) |
            # Filtrar por nombre de depósito
            Q(ID_Deposito__nombre_deposito__icontains=search_query)
        )

    # Cargar la plantilla HTML
    template = get_template('reporte_template.html')
    context = {'materiales': materiales}
    html = template.render(context)

    # Crear el PDF
    response = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), response)

    # Verificar si la generación del PDF fue exitosa
    if not pdf.err:
        # Establecer las cabeceras del HTTP response para el PDF
        response = HttpResponse(response.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="materiales_por_deposito.pdf"'
        return response

    return HttpResponse('Error al generar el PDF', status=500)

def generar_ficha_pdf(request, material_x_deposito_id):
    material_x_deposito = get_object_or_404(Material_x_Deposito, pk=material_x_deposito_id)

    # Obtener movimientos, transferencias y órdenes de trabajo y combinarlos en una lista
    movimientos = Movimiento.objects.filter(ID_MXD=material_x_deposito)
    transferencias = Transferencias.objects.filter(ID_MXD_Origen=material_x_deposito) | Transferencias.objects.filter(ID_MXD_Destino=material_x_deposito)
    ordenes_trabajo = Orden_de_trabajo.objects.filter(id_deposito=material_x_deposito.ID_Deposito)

    # Agregar atributo "tipo" para distinguir los elementos en la lista combinada
    movimientos = list(movimientos)
    for movimiento in movimientos:
        movimiento.tipo = "Movimiento"
    transferencias = list(transferencias)
    for transferencia in transferencias:
        transferencia.tipo = "Transferencia"
    ordenes_trabajo = list(ordenes_trabajo)
    for orden_trabajo in ordenes_trabajo:
        orden_trabajo.tipo = "Orden de Trabajo"

    # Combinar las listas y ordenar por fecha
    all_entries = sorted(chain(movimientos, transferencias, ordenes_trabajo), key=attrgetter('Fecha'))

    # Calcular saldo acumulado
    saldo = 0
    for entry in all_entries:
        if hasattr(entry, 'Cantidad'):
            saldo += entry.Cantidad if entry.tipo == "Movimiento" or entry.tipo == "Transferencia" else -entry.Cantidad
        entry.saldo = saldo

    context = {
        'material_x_deposito': material_x_deposito,
        'entries': all_entries,
    }

    template = get_template('ficha_pdf_template.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ficha_material_{material_x_deposito.ID_MXD}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response