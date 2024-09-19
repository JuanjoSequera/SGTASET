from django.contrib import admin
from .models import Material_x_Deposito # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	
admin.site.register(Material_x_Deposito)# -> Se registra el modelo empresa en la pagina admin 