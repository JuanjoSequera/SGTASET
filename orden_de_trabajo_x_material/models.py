from django.db import models
from material.models import Material
from orden_de_trabajo.models import Orden_de_trabajo

class OTM(models.Model):
    id_otm = models.AutoField(primary_key=True)
    id_material = models.ForeignKey(Material, on_delete=models.RESTRICT)
    nro_orden = models.ForeignKey(Orden_de_trabajo, on_delete=models.RESTRICT)
    cantidad = models.IntegerField()
    cantidad_utilizada=models.IntegerField(null=True)
    cantidad_devolver=models.IntegerField(null=True)
    
    def __str__(self):
        return f"ID_OTM: {self.id_otm}"
