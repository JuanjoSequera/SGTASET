# Generated by Django 4.2.3 on 2023-08-28 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deposito', '0005_alter_deposito_tipo_deposito'),
        ('empleado', '0006_alter_empleado_salario'),
        ('orden_de_trabajo', '0006_alter_orden_de_trabajo_descripcion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orden_de_trabajo',
            name='ID_Empleado_ayudante',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='orden_ayudante', to='empleado.empleado'),
        ),
        migrations.AlterField(
            model_name='orden_de_trabajo',
            name='ID_Empleado_tecnico',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='orden_tecnico', to='empleado.empleado'),
        ),
        migrations.AlterField(
            model_name='orden_de_trabajo',
            name='id_deposito',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='deposito.deposito'),
        ),
    ]
