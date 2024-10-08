# Generated by Django 4.2.3 on 2023-08-01 04:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empleado', '0006_alter_empleado_salario'),
        ('orden_de_trabajo', '0002_alter_orden_de_trabajo_id_empleado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orden_de_trabajo',
            name='ID_Empleado',
        ),
        migrations.AddField(
            model_name='orden_de_trabajo',
            name='Empleado_Ayudante',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='ayudante', to='empleado.empleado'),
        ),
        migrations.AddField(
            model_name='orden_de_trabajo',
            name='Empleado_Tecnico',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='tecnico', to='empleado.empleado'),
        ),
    ]
