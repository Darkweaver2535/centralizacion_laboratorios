# Generated by Django 5.2.4 on 2025-07-15 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingreso_datos', '0008_equipoindividual_unidad_academica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrera',
            name='nombre',
            field=models.CharField(choices=[('ingenieria_ambiental', 'Ingeniería Ambiental'), ('ingenieria_civil', 'Ingeniería Civil'), ('ingenieria_sistemas_electronicos', 'Ingeniería en Sistemas Electrónicos'), ('ingenieria_comercial', 'Ingeniería Comercial'), ('ingenieria_sistemas', 'Ingeniería de Sistemas'), ('ingenieria_agroindustrial', 'Ingeniería Agroindustrial'), ('sistemas_electronicos', 'Sistemas Electrónicos'), ('informatica', 'Informática'), ('construccion_civil', 'Construcción Civil'), ('energias_renovables', 'Energías Renovables'), ('diseno_grafico', 'Diseño Gráfico y Comunicación Audiovisual')], max_length=50, unique=True),
        ),
    ]
