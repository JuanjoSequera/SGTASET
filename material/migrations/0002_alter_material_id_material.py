# Generated by Django 4.2.3 on 2023-07-16 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='id_material',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
