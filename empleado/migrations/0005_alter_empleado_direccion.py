# Generated by Django 4.2.3 on 2023-07-17 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empleado', '0004_alter_empleado_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empleado',
            name='Direccion',
            field=models.CharField(max_length=100),
        ),
    ]
