import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Cliente
from .forms import ClienteForm
import csv
import io
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import hashlib
from django.contrib.messages import constants as messages_constants

def cliente_crud(request): 
    if request.user.is_authenticated:
        search_query = request.GET.get('search')
        if search_query:
            clientes = Cliente.objects.filter(numero_de_abono__icontains=search_query)
        else:
            clientes = Cliente.objects.all()

        paginator = Paginator(clientes, 15)  # Divide los clientes en páginas de 15 elementos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, 'cliente/cliente.html', context)
    else:
        return redirect('login')

def agregar(request):
	if request.user.is_authenticated:
		if request.method == "POST":
			form = ClienteForm(request.POST)
			if form.is_valid():
				form.save()
				return redirect('clientes')
		else:
			form = ClienteForm()

		context = {'form': form}
		return render(request, 'cliente/agregar.html', context)
	else:
		return redirect('login')

def borrar_clientes(request):
	if request.user.is_authenticated:
		Cliente.objects.all().delete()
		return redirect('clientes')
	else:
		return redirect('login')

def importar_csv_cliente(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            files = request.FILES.getlist('files')  # Obtener lista de archivos enviados
            registros_nuevos = []
            registros_duplicados = []
            numeros_de_abono_existentes = set(Cliente.objects.values_list('numero_de_abono', flat=True))

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
                    # Si el formato no es compatible, se omite
                    continue

            if hash_txt and rows:
                # Generar el hash SHA256 de los datos del archivo CSV
                hash_csv = hashlib.sha256(str(archivo).encode('utf-8')).hexdigest()

                if hash_txt == hash_csv:
                    for row in rows:
                        numero_de_abono = row[0]
                        nombre = row[1]
                        apellido = row[2]
                        RUC = row[3]
                        telefono = row[4]
                        direccion = row[5]

                        if numero_de_abono in numeros_de_abono_existentes:
                            registros_duplicados.append(row)
                        else:
                            # Aquí es donde se crea el objeto Cliente 
                            registros_nuevos.append(Cliente(numero_de_abono=numero_de_abono,
                                                            nombre=nombre,
                                                            apellido=apellido,
                                                            RUC=RUC,
                                                            telefono=telefono,
                                                            direccion=direccion))

                    Cliente.objects.bulk_create(registros_nuevos, ignore_conflicts=True)

                    num_registros_nuevos = len(registros_nuevos)
                    num_registros_duplicados = len(registros_duplicados)

                    # Generar el archivo CSV con los registros duplicados
                    if registros_duplicados:
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="Clientes_duplicados.csv"'

                        writer = csv.writer(response)
                        
                        for registro in registros_duplicados:
                            writer.writerow(registro)

                        url = reverse('clientes') + f"?nuevos={num_registros_nuevos}&duplicados={num_registros_duplicados}"
                            
                        # Agregar mensaje de éxito a los flash messages
                        messages.success(request, "Los archivos coinciden. <br>Registros importados con éxito y archivo CSV generado con registros duplicados.<br>La cantidad de clientes nuevos es: "+str(num_registros_nuevos)+"<br>La cantidad de clientes duplicados es: " +str(num_registros_duplicados))
                        response['Refresh'] = '1; url=cliente/clientes.html'
                        return response 

                    else:
                        url = reverse('clientes') + f"?nuevos={num_registros_nuevos}&duplicados={num_registros_duplicados}"

                        # Agregar mensaje de éxito a la cola de mensajes
                        messages.add_message(request, messages_constants.SUCCESS, "Los archivos coinciden. Registros importados con éxito.")
                        return HttpResponseRedirect(url)
                else:
                    # Los hashes no coinciden, muestra un mensaje de error
                    mensaje_error = "El archivo CSV no coincide con el hash del archivo TXT."
                    messages.add_message(request, messages_constants.ERROR, mensaje_error)
                    return HttpResponse(mensaje_error)

        else:
            return render(request, 'cliente/importar_csv.html')
    else:
        return redirect('login')
    

def actualizar_clientes(request):
        if request.user.is_authenticated:
            if request.method == "POST":
                files = request.FILES.getlist('files')  # Obtener lista de archivos enviados
                hash_txt = None
                rows = None
                registros_actualizados = 0

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
                        # Si el formato no es compatible, se omite
                        continue

                if hash_txt and rows:
                    # Generar el hash SHA256 de los datos del archivo CSV
                    hash_csv = hashlib.sha256(str(archivo).encode('utf-8')).hexdigest()

                    if hash_txt == hash_csv:
                        for row in rows:
                            numero_de_abono = row[0]
                            nombre = row[1]
                            apellido = row[2]
                            RUC = row[3]
                            telefono = row[4]
                            direccion = row[5]

                            try:
                                cliente_existente = Cliente.objects.get(numero_de_abono=numero_de_abono)

                                if (
                                    cliente_existente.nombre != nombre
                                    or cliente_existente.apellido != apellido
                                    or cliente_existente.RUC != RUC
                                    or cliente_existente.telefono != telefono
                                    or cliente_existente.direccion != direccion
                                ):
                                    cliente_existente.nombre = nombre
                                    cliente_existente.apellido = apellido
                                    cliente_existente.RUC = RUC
                                    cliente_existente.telefono = telefono
                                    cliente_existente.direccion = direccion
                                    cliente_existente.save()
                                    registros_actualizados += 1

                            except Cliente.DoesNotExist:
                                # Si no existe un cliente con el mismo número de abono en la base de datos,
                                # simplemente omite este registro 
                                pass

                        url = reverse('clientes') + f"?actualizados={registros_actualizados}"

                        # Agregar mensaje de éxito a los flash messages
                        messages.success(
                            request,
                            f"Los archivos coinciden. {registros_actualizados} registros actualizados con éxito."
                        )

                        return HttpResponseRedirect(url)

                    else:
                        # Los hashes no coinciden, muestra un mensaje de error
                        mensaje_error = "El archivo CSV no coincide con el hash del archivo TXT."
                        messages.error(request, mensaje_error)
                        return HttpResponse(mensaje_error)

            else:
                return render(request, 'cliente/actualizar_csv.html')
        else:
            return redirect('login')

