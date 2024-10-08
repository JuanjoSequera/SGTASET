# Generated by Django 4.2.3 on 2023-07-30 20:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('deposito', '0004_alter_deposito_tipo_deposito'),
        ('empleado', '0006_alter_empleado_salario'),
        ('cliente', '0002_remove_cliente_estado'),
        ('tarea', '0003_rename_tipo_tarea_nombre'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orden_de_trabajo',
            fields=[
                ('nro_orden', models.IntegerField(primary_key=True, serialize=False)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('descripcion', models.CharField(max_length=100)),
                ('observacion', models.CharField(max_length=100)),
                ('estado', models.CharField(max_length=50)),
                ('ID_Empleado', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='empleado.empleado')),
                ('ID_Tarea', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='tarea.tarea')),
                ('id_deposito', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='deposito.deposito')),
                ('numero_de_abono', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cliente.cliente')),
            ],
        ),
    ]
