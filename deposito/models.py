from django.db import models
from empleado.models import Empleado
from .choises import *


class Deposito(models.Model):
    id_deposito = models.AutoField(primary_key=True)
    ID_Empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    nombre_deposito = models.CharField(max_length=50)
    tipo_deposito = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tipo_deposito} {self.nombre_deposito}"