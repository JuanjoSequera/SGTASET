from django.contrib import admin
from .models import Cargo # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	
admin.site.register(Cargo) # -> Se registra el modelo empresa en la pagina admin 

# Register your models here.
