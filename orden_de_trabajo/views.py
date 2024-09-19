from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Orden_de_trabajo, Empleado, Tarea, Deposito, Cliente
from orden_de_trabajo_x_material.models import OTM
from material.models import Material
from material_x_deposito.models import Material_x_Deposito
import io
import csv
import hashlib
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.dateparse import parse_date
import zipfile
from django.db import transaction
from reportlab.lib.pagesizes import landscape, legal,letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.lib.units import inch  
from reportlab.pdfgen import canvas
from django.db.models import Q

from django.db.models import Q

def orden_de_trabajo_crud(request):
    if request.user.is_authenticated:
        search_query = request.GET.get('search')
        if search_query:
            # Filtrar las órdenes de trabajo por número de orden o nombre/apellido de cliente que contenga el término de búsqueda
            ordenes = Orden_de_trabajo.objects.filter(
                Q(nro_orden__icontains=search_query) |
                Q(numero_de_abono__nombre__icontains=search_query) |
                Q(numero_de_abono__apellido__icontains=search_query) |
                Q(numero_de_abono__numero_de_abono__icontains=search_query)
               
            )
        else:
             ordenes = Orden_de_trabajo.objects.filter(estado='Pendiente')


        paginator = Paginator(ordenes, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, 'orden_de_trabajo/orden_de_trabajo.html', context)
    else:
        return redirect('login')


def edicionOrden(request, nro_orden):
    orden = Orden_de_trabajo.objects.get(nro_orden=nro_orden)
    empleados = Empleado.objects.all()
    tareas = Tarea.objects.all()
    depositos = Deposito.objects.all()
    clientes = Cliente.objects.all()

    listamateriales = OTM.objects.filter(nro_orden=orden)
    

    return render(request, "orden_de_trabajo/edicionOrden.html", {
        "orden": orden,
        "empleados": empleados,
        "tareas": tareas,
        "depositos": depositos,
        "clientes": clientes,
        "listamateriales":listamateriales,

    })

def editarOrden(request, nro_orden):
    if request.method == "POST":
        empleado_tecnico_id = request.POST['empleado_tecnico']
        empleado_ayudante_id = request.POST['empleado_ayudante']
        #tarea_id = request.POST['tarea']
        deposito_id = request.POST['deposito']
        #cliente_id = request.POST['cliente']
        #fecha_inicio = request.POST['fecha_inicio']
        #fecha_fin = request.POST['fecha_fin']
        #descripcion = request.POST['descripcion']
        #observacion = request.POST['observacion']
        estado = request.POST['estado']
        
        empleado_tecnico = Empleado.objects.get(ID_Empleado=empleado_tecnico_id)
        empleado_ayudante = Empleado.objects.get(ID_Empleado=empleado_ayudante_id)
        #tarea = Tarea.objects.get(ID_Tarea=tarea_id)
        deposito = Deposito.objects.get(id_deposito=deposito_id)
        #cliente = Cliente.objects.get(numero_de_abono=cliente_id)

       # Transferir materiales del depósito principal al depósito seleccionado
        deposito_principal = Deposito.objects.get(id_deposito=1)
        listamateriales = OTM.objects.filter(nro_orden=nro_orden)
        with transaction.atomic():
            for otm in listamateriales:
                cantidad_material = otm.cantidad
                material = otm.id_material
                material_por_deposito_principal = Material_x_Deposito.objects.get(ID_Material=material, ID_Deposito=deposito_principal)
                material_por_deposito_seleccionado = Material_x_Deposito.objects.get(ID_Material=material, ID_Deposito=deposito)
                
                material_por_deposito_principal.Cantidad -= cantidad_material
                material_por_deposito_principal.save()

                material_por_deposito_seleccionado.Cantidad += cantidad_material
                material_por_deposito_seleccionado.save()
        
        orden = Orden_de_trabajo.objects.get(nro_orden=nro_orden)
        orden.ID_Empleado_tecnico= empleado_tecnico
        orden.ID_Empleado_ayudante = empleado_ayudante
        #orden.tarea = tarea
        orden.id_deposito = deposito
        #orden.numero_de_abono = cliente
        #orden.fecha_inicio = fecha_inicio
        #orden.fecha_fin = fecha_fin
        #orden.descripcion = descripcion
        #orden.observacion = observacion
        orden.estado = estado
        orden.save()

        messages.success(request, 'Orden Asignada Correctamente')
        # Redirigir al usuario a la vista que genera el PDF
        return redirect('generar_pdf_orden', nro_orden=nro_orden)

    return redirect('orden')

def importar_csv_orden(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        registros_duplicados = []
        registros_rechazados = []

        numeros_de_abono_existentes = set(Orden_de_trabajo.objects.values_list('nro_orden', flat=True))
        
        rows = None

        for file in files:
            if file.name.endswith('.csv'):
                archivo = file.read()
                decoded_file = archivo.decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                rows = list(reader)
            else:
                continue

        if rows:
            for row in rows:
                while len(row) < 17:
                    row.append('')

                nro_orden = row[0]
                ID_Tarea_id = row[1] if row[1] else None
                hoja_de_ruta = row[2]
                area_agendada = row[3]
                franquicia = row[4]
                base = row[5]
                horario = row[6]
                plan = row[7]
                numero_de_abono = row[8]
                fecha_inicio = parse_date(row[9])
                fecha_fin = parse_date(row[10])
                descripcion = row[11]
                observacion = row[12]
                estado = row[13]

                try:
                    tarea = Tarea.objects.get(pk=ID_Tarea_id)
                    cliente = Cliente.objects.get(numero_de_abono=numero_de_abono)
                except (Tarea.DoesNotExist, Cliente.DoesNotExist):
                    continue

                if int(nro_orden) in numeros_de_abono_existentes:
                    registros_duplicados.append(row)
                else:
                    orden_rechazada = False
                    for i in range(14, len(row), 2):
                        id_material = int(row[i])
                        cantidad = int(row[i + 1])

                        try:
                            material_x_deposito = Material_x_Deposito.objects.get(ID_Material=id_material)
                        except Material_x_Deposito.DoesNotExist:
                            registros_rechazados.append((nro_orden, tarea, hoja_de_ruta, area_agendada, franquicia, base, horario, plan, cliente, fecha_inicio, fecha_fin, descripcion, observacion, "Rechazado", id_material, cantidad))
                            orden_rechazada = True
                            break

                        if cantidad > material_x_deposito.Cantidad:
                            registros_rechazados.append((nro_orden, tarea, hoja_de_ruta, area_agendada, franquicia, base, horario, plan, cliente, fecha_inicio, fecha_fin, descripcion, observacion, "Rechazado", id_material, cantidad))
                            orden_rechazada = True
                            break

                    if not orden_rechazada:
                        orden = Orden_de_trabajo(
                            nro_orden=nro_orden,
                            ID_Tarea=tarea,
                            hoja_de_ruta=hoja_de_ruta,
                            area_agendada=area_agendada,
                            franquicia=franquicia,
                            base=base,
                            horario=horario,
                            plan=plan,
                            numero_de_abono=cliente,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            descripcion=descripcion,
                            observacion=observacion,
                            estado=estado
                        )
                        orden.save()

                        for i in range(14, len(row), 2):
                            id_material = int(row[i])
                            cantidad = int(row[i + 1])

                            material_instance = Material.objects.get(pk=id_material)

                            OTM.objects.create(
                                id_material=material_instance,
                                nro_orden=orden,
                                cantidad=cantidad
                            )
            
            num_registros_duplicados = len(registros_duplicados)
            num_registros_rechazados = len(registros_rechazados)

            if registros_duplicados or registros_rechazados:
                # Crear archivo CSV de duplicados si existen
                if registros_duplicados:
                    response_duplicados = HttpResponse(content_type='text/csv')
                    response_duplicados['Content-Disposition'] = 'attachment; filename="Ordenes_duplicados.csv"'

                    writer_duplicados = csv.writer(response_duplicados)
                    for registro in registros_duplicados:
                        writer_duplicados.writerow(registro)

                    # Generar hash para el archivo de duplicados
                    hash_value_duplicados = hashlib.sha256(str(response_duplicados).encode('utf-8')).hexdigest()

                    hash_file_name_duplicados = 'Ordenes_duplicados_hash.txt'
                    with open(hash_file_name_duplicados, 'w') as hash_file:
                        hash_file.write(hash_value_duplicados)

                # Crear archivo CSV de rechazados si existen
                if registros_rechazados:
                    response_rechazados = HttpResponse(content_type='text/csv')
                    response_rechazados['Content-Disposition'] = 'attachment; filename="Ordenes_rechazadas.csv"'

                    writer_rechazados = csv.writer(response_rechazados)
                    for registro in registros_rechazados:
                        writer_rechazados.writerow(registro)

                    # Generar hash para el archivo de rechazados
                    hash_value_rechazados = hashlib.sha256(str(response_rechazados).encode('utf-8')).hexdigest()

                    hash_file_name_rechazados = 'Ordenes_rechazadas_hash.txt'
                    with open(hash_file_name_rechazados, 'w') as hash_file:
                        hash_file.write(hash_value_rechazados)

                # Crear archivo ZIP con los archivos CSV y sus hashes si hay ambos archivos
                if registros_duplicados and registros_rechazados:
                    with BytesIO() as zip_buffer:
                        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                            zipf.writestr("Ordenes_duplicados.csv", response_duplicados.getvalue())
                            zipf.writestr("Ordenes_duplicados_hash.txt", hash_value_duplicados)
                            zipf.writestr("Ordenes_rechazadas.csv", response_rechazados.getvalue())
                            zipf.writestr("Ordenes_rechazadas_hash.txt", hash_value_rechazados)

                        response_zip = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                        response_zip['Content-Disposition'] = 'attachment; filename="Ordenes_rechazadas_duplicados.zip"'
                        return response_zip
                else:
                    # Descargar archivo CSV individual junto con su hash si solo hay uno
                    if registros_duplicados:
                        response_csv = response_duplicados
                        hash_value = hash_value_duplicados
                        hash_file_name = hash_file_name_duplicados
                        archivo_nombre = "duplicados"
                    else:
                        response_csv = response_rechazados
                        hash_value = hash_value_rechazados
                        hash_file_name = hash_file_name_rechazados
                        archivo_nombre = "rechazados"

                    response_csv['Content-Disposition'] = f'attachment; filename="{response_csv["Content-Disposition"].split("=")[1][1:-1]}"'

                    with open(hash_file_name, 'w') as hash_file:
                        hash_file.write(hash_value)

                    responses = [(response_csv, hash_value, hash_file_name)]

                    # Crear archivo ZIP con el archivo CSV y su hash
                    with BytesIO() as zip_buffer:
                        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                            for response_csv, hash_value, hash_file_name in responses:
                                zipf.writestr(f"Archivo_{archivo_nombre}.csv", response_csv.getvalue())
                                zipf.writestr(f"Archivo_{archivo_nombre}_hash.txt", hash_value)

                        response_zip = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                        response_zip['Content-Disposition'] = f'attachment; filename="Archivo_{archivo_nombre}_zip.zip"'

                    messages.success(request, f"Se generó un archivo {response_csv['Content-Disposition'].split('=')[1][1:-1]} con su hash correspondiente. <br>Cantidad de rechazados: {num_registros_rechazados}, <br>Cantidad de duplicados: {num_registros_duplicados}")

                    return response_zip
            else:
                messages.success(request, "Los archivos coinciden. No se encontraron registros duplicados ni rechazados.")
                return HttpResponseRedirect(reverse('orden'))
        else:
            return render(request, 'orden/importar_csv_orden.html')
    else:
        return redirect('login')


def generar_pdf_orden(request, nro_orden):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orden_{nro_orden}.pdf"'

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=legal, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    orden = Orden_de_trabajo.objects.get(nro_orden=nro_orden)
    listamateriales = OTM.objects.filter(nro_orden=orden)

    elements = []

    elements.append(Paragraph('Orden de Trabajo', styles['Title']))

    # Agregar espacio entre el título y los datos de la orden
    elements.append(Spacer(1, 24))  # Espacio de 2 renglones

    data = [
        [Paragraph('<b>Tarea:</b>' ), orden.ID_Tarea.Nombre, Paragraph('<b>Número de Orden:</b>'), str(orden.nro_orden)],
        [Paragraph('<b>Franquicia:</b>'), orden.franquicia, Paragraph('<b>Base:</b>' ), orden.base],
        [Paragraph('<b>Área de Agenda:</b>' ), orden.area_agendada, Paragraph('<b>MGT:</b>' ), orden.hoja_de_ruta],
        [Paragraph('<b>Fecha de Inicio:</b>' ), str(orden.fecha_inicio), Paragraph('<b>Horario:</b>'), orden.horario, Paragraph('<b>Depósito:</b>' ), orden.id_deposito.nombre_deposito],
        [Paragraph('<b>Técnico:</b>' ), f'{orden.ID_Empleado_tecnico.Nombre} {orden.ID_Empleado_tecnico.Apellido}', Paragraph('<b>Ayudante:</b>' ), f'{orden.ID_Empleado_ayudante.Nombre} {orden.ID_Empleado_ayudante.Apellido}'],
        [Paragraph('<b>N° de Abonado</b>:'), f'{orden.numero_de_abono.numero_de_abono}', Paragraph('<b>Nombre:</b>:'), f'{orden.numero_de_abono.nombre} {orden.numero_de_abono.apellido}', Paragraph('<b>Telefono:</b>'), f'{orden.numero_de_abono.telefono}'],
        [Paragraph('<b>Direccion</b>:'), f'{orden.numero_de_abono.direccion}', Paragraph('<b>Plan</b>:'), f'{orden.plan}'],
        [Paragraph('<b>Descripcion</b>:'), f'{orden.descripcion}']
    ]

    table = Table(data, colWidths=[100, 100, 100, 100])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0,0), 'LEFT'),
    ]))
    elements.append(table)

    # Agregar espacio entre el título y los datos de la orden
    elements.append(Spacer(1, 24))  # Espacio de 2 renglones
    
    # Agregar lista de materiales
    elements.append(Paragraph('Lista de Materiales:', styles['Title']))
    # Agregar espacio entre el título y los datos de la orden
    elements.append(Spacer(1, 24))  # Espacio de 2 renglones

    data = [['Material', 'Cantidad']]
    for material in listamateriales:
        data.append([material.id_material.nombre_material, str(material.cantidad)])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    elements.append(table)

    # Agregar espacio entre el título y los datos de la orden
    elements.append(Spacer(1, 24))  # Espacio de 2 renglones

   # Agregar observación
    elements.append(Spacer(1, 20))  # Espacio antes de la sección de observación
    elements.append(Paragraph('Observación:', styles['Heading2']))
    
    # Agregar espacio entre el título y los datos de la orden
    elements.append(Spacer(1, 24))  # Espacio de 2 renglones

    elements.append(Spacer(1, 20))  # Espacio antes de la línea de firma
    #Agregar la línea de firma y el texto "Firma del Cliente"
    firma_table = Table([
        ['-' * 50],
        ['Firma del Cliente']
    ])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(firma_table)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

def ot_en_progreso_crud(request):
    if request.user.is_authenticated:
        search_query = request.GET.get('search')
        if search_query:
            # Filtrar las órdenes de trabajo por número de orden o nombre/apellido de cliente que contenga el término de búsqueda
            ordenes = Orden_de_trabajo.objects.filter(
                Q(nro_orden__icontains=search_query) |
                Q(numero_de_abono__nombre__icontains=search_query) |
                Q(numero_de_abono__apellido__icontains=search_query) |
                Q(numero_de_abono__numero_de_abono__icontains=search_query)
               
            )
        else:
           ordenes = Orden_de_trabajo.objects.filter(estado='En Progreso')

        paginator = Paginator(ordenes, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, 'orden_de_trabajo/ot_en_progreso.html', context)
    else:
        return redirect('login')


def terminarOrden(request, nro_orden):
    orden = Orden_de_trabajo.objects.get(nro_orden=nro_orden)
    empleados = Empleado.objects.all()
    tareas = Tarea.objects.all()
    depositos = Deposito.objects.all()
    clientes = Cliente.objects.all()

    listamateriales = OTM.objects.filter(nro_orden=orden)
    

    return render(request, "orden_de_trabajo/terminarOT.html", {
        "orden": orden,
        "empleados": empleados,
        "tareas": tareas,
        "depositos": depositos,
        "clientes": clientes,
        "listamateriales":listamateriales,

    })
def dardebajaOrden(request, nro_orden):
    if request.method == "POST":
        #empleado_tecnico_id = request.POST['empleado_tecnico']
        #empleado_ayudante_id = request.POST['empleado_ayudante']
        #tarea_id = request.POST['tarea']
        #deposito_id = request.POST['deposito']
        #cliente_id = request.POST['cliente']
        #fecha_inicio = request.POST['fecha_inicio']
        #fecha_fin = request.POST['fecha_fin']
        #descripcion = request.POST['descripcion']
        #observacion = request.POST['observacion']
        estado = request.POST['estado']
        
        #empleado_tecnico = Empleado.objects.get(ID_Empleado=empleado_tecnico_id)
        #empleado_ayudante = Empleado.objects.get(ID_Empleado=empleado_ayudante_id)
        #tarea = Tarea.objects.get(ID_Tarea=tarea_id)
        #deposito = Deposito.objects.get(id_deposito=deposito_id)
        #cliente = Cliente.objects.get(numero_de_abono=cliente_id)

       # Transferir materiales sobrantes al depsoito principal
        deposito_principal = Deposito.objects.get(id_deposito=1)
        listamateriales = OTM.objects.filter(nro_orden=nro_orden)

        with transaction.atomic():
            for listamaterial in listamateriales:
                
                material_id = listamaterial.id_material
                cantidad_utilizada = int(request.POST.get('cantidad_utilizada_{}'.format(material_id)))
                cantidad_disponible = listamaterial.cantidad

                if cantidad_utilizada > 0:
                    cantidad_devolver = cantidad_disponible - cantidad_utilizada
                    if cantidad_devolver < 0:
                        cantidad_devolver = 0

                    listamaterial.cantidad_devolver = cantidad_devolver
                    listamaterial.cantidad_utilizada = cantidad_utilizada
                    listamaterial.save()

                    # Actualizar la cantidad en Materiales_x_Deposito
                    material_por_deposito = Material_x_Deposito.objects.get(ID_Material=material_id, ID_Deposito=1)
                    material_por_deposito.Cantidad += cantidad_devolver
                    material_por_deposito.save()
        
        orden = Orden_de_trabajo.objects.get(nro_orden=nro_orden)
        #orden.ID_Empleado_tecnico= empleado_tecnico
        #orden.ID_Empleado_ayudante = empleado_ayudante
        #orden.tarea = tarea
        #orden.id_deposito = deposito
        #orden.numero_de_abono = cliente
        #orden.fecha_inicio = fecha_inicio
        #orden.fecha_fin = fecha_fin
        #orden.descripcion = descripcion
        #orden.observacion = observacion
        orden.estado = estado
        orden.save()

    return redirect('orden_progreso')


def ot_terminada_crud(request):
    if request.user.is_authenticated:
        search_query = request.GET.get('search')
        if search_query:
            # Filtrar las órdenes de trabajo por número de orden o nombre/apellido de cliente que contenga el término de búsqueda
            ordenes = Orden_de_trabajo.objects.filter(
                Q(nro_orden__icontains=search_query) |
                Q(numero_de_abono__nombre__icontains=search_query) |
                Q(numero_de_abono__apellido__icontains=search_query) |
                Q(numero_de_abono__numero_de_abono__icontains=search_query)
               
            )
        else:
             ordenes = Orden_de_trabajo.objects.filter(estado='Terminado')


        paginator = Paginator(ordenes, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, 'orden_de_trabajo/ot_terminada.html', context)
    else:
        return redirect('login')
    
def ot_rechazado_crud(request):
    if request.user.is_authenticated:
        search_query = request.GET.get('search')
        if search_query:
            # Filtrar las órdenes de trabajo por número de orden o nombre/apellido de cliente que contenga el término de búsqueda
            ordenes = Orden_de_trabajo.objects.filter(
                Q(nro_orden__icontains=search_query) |
                Q(numero_de_abono__nombre__icontains=search_query) |
                Q(numero_de_abono__apellido__icontains=search_query) |
                Q(numero_de_abono__numero_de_abono__icontains=search_query)
               
            )
        else:
             ordenes = Orden_de_trabajo.objects.filter(estado='Rechazado')


        paginator = Paginator(ordenes, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, 'orden_de_trabajo/ot_rechazada.html', context)
    else:
        return redirect('login')