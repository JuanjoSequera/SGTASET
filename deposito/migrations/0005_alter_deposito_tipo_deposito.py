# Generated by Django 4.2.3 on 2023-08-28 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposito', '0004_alter_deposito_tipo_deposito'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposito',
            name='tipo_deposito',
            field=models.CharField(max_length=50),
        ),
    ]
