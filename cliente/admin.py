from django.contrib import admin
from .models import Cliente # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	
admin.site.register(Cliente) # -> Se registra el modelo empresa en la pagina admin 