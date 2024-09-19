import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Material
from material_x_deposito.models import Material_x_Deposito
from deposito.models import Deposito
from .forms import MaterialForm
import csv
import io
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import hashlib
from django.contrib.messages import constants as messages_constants


def material_crud(request): 
    if request.user.is_authenticated:
        search_query = request.GET.get('search')
        if search_query:
            materiales = Material.objects.filter(codigo_fabricante__icontains=search_query)
        else:
            materiales = Material.objects.all()

        paginator = Paginator(materiales, 15)  # Divide los materiales en páginas de 15 elementos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, 'material/material.html', context)
    else:
        return redirect('login')

def agregar(request):
	if request.user.is_authenticated:
		if request.method == "POST":
			form = MaterialForm(request.POST)
			if form.is_valid():
				form.save()
				return redirect('materiales')
		else:
			form = MaterialForm()

		context = {'form': form}
		return render(request, 'material/agregar.html', context)
	else:
		return redirect('login')

def borrar_materiales(request):
	if request.user.is_authenticated:
		Material.objects.all().delete()
		return redirect('materiales')
	else:
		return redirect('login')

def importar_csv(request):
    
    if request.user.is_authenticated:
        if request.method == "POST":
            files = request.FILES.getlist('files')  # Obtener lista de archivos enviados
            registros_nuevos = []
            registros_duplicados = []
            codigos_fabricante_existentes = set(Material.objects.values_list('codigo_fabricante', flat=True))

            hash_txt = None
            rows = None

            for file in files:
                # Leer el archivo dependiendo de su formato
                if file.name.endswith('.csv'):
                    archivo = file.read()
                    decoded_file = archivo.decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    reader = csv.reader(io_string)
                    rows = list(reader)
                elif file.name.endswith('.txt'):
                    # Leer el archivo TXT y obtener el hash almacenado
                    hash_txt = file.read().decode('utf-8').strip()  # Suponemos que el hash está en la primera línea del archivo
                else:
                    # Si el formato no es compatible, puedes manejarlo según tus necesidades
                    # Aquí se omite, pero puedes agregar un mensaje de error o simplemente ignorarlo
                    continue

            if hash_txt and rows:
                # Generar el hash SHA256 de los datos del archivo CSV
                hash_csv = hashlib.sha256(str(archivo).encode('utf-8')).hexdigest()

                if hash_txt == hash_csv:
                    for row in rows:
                        codigo_fabricante = row[0]
                        if codigo_fabricante in codigos_fabricante_existentes:
                            registros_duplicados.append(row)
                        else:
                            # Aquí es donde se crea el objeto Material sin los campos 'nro_serial' y 'nro_tarjeta'
                            registros_nuevos.append(Material(codigo_fabricante=codigo_fabricante,nombre_material=row[1]))

                    Material.objects.bulk_create(registros_nuevos, ignore_conflicts=True)

                    num_registros_nuevos = len(registros_nuevos)
                    num_registros_duplicados = len(registros_duplicados)

                    # Crear objetos Material_x_Deposito para cada combinación de material y depósito
                    nuevos_materiales = Material.objects.all()
                    nuevos_depositos = Deposito.objects.all()

                    nuevos_material_x_deposito = []

                    for material in nuevos_materiales:
                        for deposito in nuevos_depositos:
                            existe_material_x_deposito = Material_x_Deposito.objects.filter(ID_Material=material, ID_Deposito=deposito).exists()

                            if not existe_material_x_deposito:
                                nuevo_material_x_deposito = Material_x_Deposito(
                                    ID_Material=material,
                                    ID_Deposito=deposito,
                                    Cantidad=0,  # Cantidad inicial
                                    Stock_min=10,
                                    Stock_max=20,
                                    Unidad_medida='Unidad'  # Actualiza esto según tus necesidades
                                )
                                nuevos_material_x_deposito.append(nuevo_material_x_deposito)

                    Material_x_Deposito.objects.bulk_create(nuevos_material_x_deposito)

                    # Generar el archivo CSV con los registros duplicados
                    if registros_duplicados:
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="Materiales_duplicados.csv"'

                        writer = csv.writer(response)
                        
                        for registro in registros_duplicados:
                            writer.writerow(registro)

                        url = reverse('materiales') + f"?nuevos={num_registros_nuevos}&duplicados={num_registros_duplicados}"
                            
                        # Agregar mensaje de éxito a los flash messages
                        messages.success(request, "Los archivos coinciden. <br>Registros importados con éxito y archivo CSV generado con registros duplicados.<br>La cantidad de materiales nuevos es: "+str(num_registros_nuevos)+"<br>La cantidad de materiales duplicados es: " +str(num_registros_duplicados))
                        response['Refresh'] = '1; url=material/materiales.html'
                        return response

                    else:
                        url = reverse('materiales') + f"?nuevos={num_registros_nuevos}&duplicados={num_registros_duplicados}"

                        # Agregar mensaje de éxito a la cola de mensajes
                        messages.add_message(request, messages_constants.SUCCESS, "Los archivos coinciden. Registros importados con éxito.")
                        return HttpResponseRedirect(url)

                else:
                    # Los hashes no coinciden, muestra un mensaje de error
                    mensaje_error = "El archivo CSV no coincide con el hash del archivo TXT."
                    messages.add_message(request, messages_constants.ERROR, mensaje_error)
                    return HttpResponse(mensaje_error)

        else:
            return render(request, 'material/importar_csv.html')
    else:
        return redirect('login')
