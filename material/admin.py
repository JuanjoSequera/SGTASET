from django.contrib import admin
from .models import Material # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	
admin.site.register(Material) # -> Se registra el modelo empresa en la pagina admin 