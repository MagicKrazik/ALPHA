# Generated by Django 5.1.2 on 2024-11-05 00:17

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_contactmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id_paciente', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID Paciente')),
                ('folio_hospitalizacion', models.CharField(max_length=50, unique=True, verbose_name='Folio Hospitalización')),
                ('nombres', models.CharField(max_length=100, verbose_name='Nombres')),
                ('apellidos', models.CharField(max_length=100, verbose_name='Apellidos')),
                ('fecha_nacimiento', models.DateField(verbose_name='Fecha de Nacimiento')),
                ('codigo_barras', models.ImageField(upload_to='codigos_barra/%Y/%m/', verbose_name='Código de Barras')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
                ('ultima_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('medico', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Médico Tratante')),
            ],
            options={
                'verbose_name': 'Paciente',
                'verbose_name_plural': 'Pacientes',
                'ordering': ['-fecha_registro'],
                'indexes': [models.Index(fields=['folio_hospitalizacion'], name='website_pat_folio_h_16dffc_idx'), models.Index(fields=['medico', 'fecha_registro'], name='website_pat_medico__df718d_idx')],
            },
        ),
    ]
