from django.contrib import admin

from .models import OTM # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	
admin.site.register(OTM)# -> Se registra el modelo empresa en la pagina admin 
