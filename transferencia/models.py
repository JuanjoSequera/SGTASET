from django.db import models
from material_x_deposito.models import Material_x_Deposito
from empleado.models import Empleado
from datetime import datetime

class Transferencias(models.Model):
    ID_Transferencias = models.AutoField(primary_key=True)
    ID_MXD_Origen = models.ForeignKey(Material_x_Deposito, on_delete=models.RESTRICT, related_name='Origen')
    ID_MXD_Destino = models.ForeignKey(Material_x_Deposito, on_delete=models.RESTRICT, related_name='Destino')
    ID_Empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    Fecha = models.DateField(default=datetime.now)
    Cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.ID_MXD_Origen} / {self.ID_MXD_Destino}"
