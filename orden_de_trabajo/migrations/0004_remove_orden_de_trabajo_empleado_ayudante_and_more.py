# Generated by Django 4.2.3 on 2023-08-01 04:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empleado', '0006_alter_empleado_salario'),
        ('orden_de_trabajo', '0003_remove_orden_de_trabajo_id_empleado_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orden_de_trabajo',
            name='Empleado_Ayudante',
        ),
        migrations.RemoveField(
            model_name='orden_de_trabajo',
            name='Empleado_Tecnico',
        ),
        migrations.AddField(
            model_name='orden_de_trabajo',
            name='ID_Empleado_ayudante',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='orden_ayudante', to='empleado.empleado'),
        ),
        migrations.AddField(
            model_name='orden_de_trabajo',
            name='ID_Empleado_tecnico',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='orden_tecnico', to='empleado.empleado'),
        ),
    ]
