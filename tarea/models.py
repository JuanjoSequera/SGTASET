from django.db import models
from .choises import *

# Create your models here.
class Tarea(models.Model):     
    ID_Tarea = models.AutoField(primary_key=True)     
    Nombre = models.CharField(max_length=50)      
    
    def __str__(self):
        texto ="{0} ({1})"
        return texto.format(self.Nombre, self.ID_Tarea)