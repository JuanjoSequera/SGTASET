from django.contrib import admin
from .models import Tarea # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	
admin.site.register(Tarea) # -> Se registra el modelo empresa en la pagina admin 

# Register your models here.
