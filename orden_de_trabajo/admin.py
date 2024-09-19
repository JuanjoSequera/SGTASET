from django.contrib import admin

from .models import Orden_de_trabajo # -> Trata de acceder al archivo models y importar la clase "Empresa" creada
	

admin.site.register(Orden_de_trabajo)# -> Se registra el modelo empresa en la pagina admin 
 