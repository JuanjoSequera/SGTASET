from django.db import models
from material.models import Material
from deposito.models import Deposito


class Material_x_Deposito(models.Model):
    ID_MXD = models.AutoField(primary_key=True)
    ID_Material = models.ForeignKey(Material, on_delete=models.RESTRICT)
    ID_Deposito = models.ForeignKey(Deposito, on_delete=models.RESTRICT)
    Cantidad = models.IntegerField()
    Stock_min = models.PositiveIntegerField()
    Stock_max = models.PositiveIntegerField()
    Unidad_medida = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.ID_Material} - {self.ID_Deposito}"
