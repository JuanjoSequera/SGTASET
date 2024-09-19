from django.db import models

class Material(models.Model):
    id_material = models.IntegerField(primary_key=True)
    codigo_fabricante = models.CharField(max_length=100)
    nombre_material = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre_material