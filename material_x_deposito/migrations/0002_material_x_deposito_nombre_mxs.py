# Generated by Django 4.2.3 on 2023-07-18 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material_x_deposito', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='material_x_deposito',
            name='Nombre_MXS',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
