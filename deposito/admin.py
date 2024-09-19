from django.contrib import admin
from .models import Deposito # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	
admin.site.register(Deposito)# -> Se registra el modelo empresa en la pagina admin 