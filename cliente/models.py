from django.db import models

# Create your models here.

class Cliente(models.Model):
    numero_de_abono = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    RUC = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    

    def __str__(self):
        return self.numero_de_abono