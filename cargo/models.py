from django.db import models


class Cargo(models.Model):
    id_cargo = models.IntegerField(primary_key=True)
    nombre_cargo = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_cargo

