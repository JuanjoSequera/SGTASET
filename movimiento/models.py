from django.db import models
from empleado.models import Empleado
from material_x_deposito.models import Material_x_Deposito
from datetime import datetime
Signo = (
    (1, 'Entrada'),
    (-1, 'Salida')
)

class Movimiento(models.Model):
    ID_Movimiento = models.AutoField(primary_key=True)
    ID_MXD = models.ForeignKey(Material_x_Deposito, on_delete=models.RESTRICT)
    ID_Empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    Concepto = models.CharField(max_length=100)
    Cantidad = models.IntegerField()
    Fecha = models.DateField(default=datetime.now)
    Signo = models.IntegerField(choices=Signo)

    def __str__(self):
        return f"{self.ID_MXD.ID_Material.nombre_material} - {self.ID_MXD.ID_Deposito.nombre_deposito}"
