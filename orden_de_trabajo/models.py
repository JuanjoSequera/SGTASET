from django.db import models
from empleado.models import Empleado
from tarea.models import Tarea
from deposito.models import Deposito
from cliente.models import Cliente


class Orden_de_trabajo(models.Model):
    nro_orden = models.IntegerField(primary_key=True)
    ID_Empleado_tecnico = models.ForeignKey(Empleado, null=True, blank=True, on_delete=models.RESTRICT, related_name="orden_tecnico")
    ID_Empleado_ayudante = models.ForeignKey(Empleado, null=True, blank=True, on_delete=models.RESTRICT, related_name="orden_ayudante")
    ID_Tarea = models.ForeignKey(Tarea, on_delete=models.RESTRICT)
    id_deposito = models.ForeignKey(Deposito, null=True, blank=True, on_delete=models.RESTRICT)
    numero_de_abono = models.ForeignKey(Cliente, on_delete=models.RESTRICT)
    hoja_de_ruta=models.CharField(max_length=100,null=True)
    area_agendada=models.CharField(max_length=100,null=True)
    franquicia=models.CharField(max_length=100,null=True)
    base=models.CharField(max_length=100,null=True)
    horario=models.CharField(max_length=100,null=True)
    plan=models.CharField(max_length=100,null=True)
    fecha_inicio=models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.CharField(max_length=100,null=True)
    observacion = models.CharField(max_length=100,null=True)
    estado = models.CharField(max_length=50)

    