from django.db import models
from .choises import *
from cargo.models import Cargo

# Create your models here.
class Empleado(models.Model):
    ID_Empleado = models.AutoField(primary_key=True)
    ID_Cargo = models.ForeignKey(Cargo, null=True, blank=True, on_delete=models.RESTRICT)
    Nombre = models.CharField(max_length=50)
    Apellido = models.CharField(max_length=50)
    CI = models.PositiveIntegerField()
    Telefono = models.PositiveIntegerField()
    Direccion = models.CharField(max_length=100)
    Mail = models.CharField(max_length=50)
    Salario = models.CharField(max_length=50)
    Estado = models.CharField(max_length=50, choices=Estado, default='Activo')

    def __str__(self):
        return f"{self.Nombre} {self.Apellido}"