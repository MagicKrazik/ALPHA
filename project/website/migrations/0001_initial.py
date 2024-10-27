# Generated by Django 5.1.2 on 2024-10-27 05:32

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreSurgeryForm',
            fields=[
                ('folio_hospitalizacion', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='Folio Hospitalización')),
                ('nombres', models.CharField(max_length=100, verbose_name='Nombres')),
                ('apellidos', models.CharField(max_length=100, verbose_name='Apellidos')),
                ('medico', models.CharField(max_length=100, verbose_name='Médico')),
                ('fecha_nacimiento', models.DateField(verbose_name='Fecha de Nacimiento')),
                ('codigo_barras', models.ImageField(upload_to='codigos_barra/', verbose_name='Código de Barras')),
                ('fecha_reporte', models.DateField(verbose_name='Fecha de Reporte')),
                ('medico_tratante', models.CharField(max_length=100, verbose_name='Médico Tratante')),
                ('diagnostico_preoperatorio', models.TextField(verbose_name='Diagnóstico Preoperatorio')),
                ('peso', models.IntegerField(verbose_name='Peso (kg)')),
                ('talla', models.IntegerField(verbose_name='Talla (cm)')),
                ('imc', models.IntegerField(verbose_name='IMC')),
                ('estado_fisico_asa', models.IntegerField(choices=[(1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV'), (5, 'V'), (6, 'VI')], verbose_name='Estado Físico ASA')),
                ('comorbilidades', models.TextField(blank=True, verbose_name='Comorbilidades')),
                ('medicamentos', models.TextField(blank=True, verbose_name='Medicamentos')),
                ('ayuno_hrs', models.IntegerField(verbose_name='Ayuno (hrs)')),
                ('uso_glp1', models.BooleanField(default=False, verbose_name='Uso de GLP1')),
                ('dosis_glp1', models.CharField(blank=True, max_length=50, verbose_name='Dosis GLP1')),
                ('alergias', models.TextField(blank=True, verbose_name='Alergias')),
                ('tabaquismo', models.BooleanField(default=False, verbose_name='Tabaquismo')),
                ('antecedentes_dificultad', models.BooleanField(default=False, verbose_name='Antecedentes de Dificultad de Manejo')),
                ('descripcion_dificultad', models.TextField(blank=True, verbose_name='Descripción de Dificultad')),
                ('evaluacion_preoperatoria', models.TextField(verbose_name='Evaluación Preoperatoria')),
                ('estudios_radiologicos_va', models.ImageField(blank=True, upload_to='estudios_radiologicos/', verbose_name='Estudios Radiológicos VA')),
                ('uso_usg_gastrico', models.BooleanField(default=False, verbose_name='Uso de USG Gástrico')),
                ('usg_gastrico_ml', models.IntegerField(blank=True, null=True, verbose_name='USG Gástrico (ml)')),
                ('imagen_usg_gastrico', models.ImageField(blank=True, upload_to='usg_gastrico/', verbose_name='Imagen USG Gástrico')),
                ('fc', models.IntegerField(verbose_name='FC')),
                ('ta', models.IntegerField(verbose_name='TA')),
                ('spo2_aire', models.IntegerField(verbose_name='SpO2 Aire Ambiente')),
                ('spo2_oxigeno', models.IntegerField(verbose_name='SpO2 con Oxígeno')),
                ('glasgow', models.IntegerField(verbose_name='Glasgow')),
                ('mallampati', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Mallampati')),
                ('patil_aldrete', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Patil-Aldrete')),
                ('distancia_inter_incisiva', models.FloatField(verbose_name='Distancia Inter-incisiva (cm)')),
                ('distancia_tiro_mentoniana', models.FloatField(verbose_name='Distancia Tiro-mentoniana (cm)')),
                ('protrusion_mandibular', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Protrusión Mandibular')),
                ('macocha', models.IntegerField(verbose_name='Macocha')),
                ('stop_bang', models.IntegerField(verbose_name='Stop Bang')),
                ('desviacion_traquea', models.IntegerField(verbose_name='Desviación de la Tráquea (cm)')),
                ('problemas_deglucion', models.BooleanField(default=False, verbose_name='Problemas de Deglución')),
                ('estridor_laringeo', models.BooleanField(default=False, verbose_name='Estridor Laríngeo')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
            ],
            options={
                'verbose_name': 'Pre-Surgery Form',
                'verbose_name_plural': 'Pre-Surgery Forms',
            },
        ),
        migrations.CreateModel(
            name='MedicoUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(error_messages={'unique': 'Ya existe un usuario con este nombre.'}, help_text='Requerido. 150 caracteres o menos. Letras, números, puntos y guiones bajos solamente.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='usuario')),
                ('email', models.EmailField(error_messages={'unique': 'Ya existe un usuario con este correo electrónico.'}, max_length=254, unique=True, verbose_name='email address')),
                ('nombre', models.CharField(help_text='Nombres del médico', max_length=100, verbose_name='nombre')),
                ('apellidos', models.CharField(help_text='Apellidos del médico', max_length=100, verbose_name='apellidos')),
                ('telefono', models.CharField(help_text='Número de contacto del médico', max_length=17, verbose_name='teléfono')),
                ('especialidad', models.CharField(choices=[('ANE', 'Anestesiología'), ('ANP', 'Anestesiología Pediátrica'), ('MEC', 'Medicina Crítica'), ('MED', 'Medicina del Dolor'), ('OTR', 'Otra Especialidad')], default='ANE', max_length=3, verbose_name='especialidad')),
                ('is_verified', models.BooleanField(default=False, verbose_name='verificado')),
                ('date_verified', models.DateTimeField(blank=True, null=True, verbose_name='fecha de verificación')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'médico',
                'verbose_name_plural': 'médicos',
                'swappable': 'AUTH_USER_MODEL',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='PostDuringSurgeryForm',
            fields=[
                ('folio_hospitalizacion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='website.presurgeryform', verbose_name='Folio Hospitalización')),
                ('lugar_problema', models.CharField(max_length=200, verbose_name='Lugar o Área del Problema')),
                ('presencia_anestesiologo', models.BooleanField(verbose_name='Presencia de Anestesiólogo')),
                ('tecnica_utilizada', models.CharField(max_length=200, verbose_name='Técnica Utilizada')),
                ('carro_via_aerea', models.BooleanField(verbose_name='Carro de Vía Aérea Difícil Disponible')),
                ('tipo_video_laringoscopia', models.CharField(blank=True, max_length=100, verbose_name='Tipo de Video-laringoscopía')),
                ('video_laringoscopia', models.FileField(blank=True, upload_to='video_laringoscopia/', verbose_name='Video de Laringoscopía')),
                ('clasificacion_han', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)], verbose_name='Clasificación HAN')),
                ('aditamento_via_aerea', models.CharField(max_length=200, verbose_name='Aditamento de Vía Aérea')),
                ('tiempo_preoxigenacion', models.IntegerField(verbose_name='Tiempo de Pre-oxigenación (minutos)')),
                ('uso_supraglotico', models.BooleanField(verbose_name='Uso de Supraglótico')),
                ('tipo_supraglotico', models.CharField(blank=True, max_length=100, verbose_name='Tipo de Supraglótico')),
                ('problemas_supragloticos', models.TextField(blank=True, verbose_name='Problemas con Supraglóticos')),
                ('tipo_intubacion', models.CharField(max_length=100, verbose_name='Tipo de Intubación')),
                ('numero_intentos', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Número de Intentos')),
                ('laringoscopia_directa', models.TextField(verbose_name='Laringoscopía Directa')),
                ('cormack', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Cormack')),
                ('pogo', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='POGO (%)')),
                ('intubacion_tecnica_mixta', models.CharField(blank=True, max_length=200, verbose_name='Intubación Técnica Mixta')),
                ('intubacion_despierto', models.BooleanField(verbose_name='Intubación Despierto')),
                ('descripcion_intubacion_despierto', models.TextField(blank=True, verbose_name='Descripción Intubación Despierto')),
                ('tipo_anestesia', models.CharField(max_length=200, verbose_name='Tipo de Anestesia')),
                ('sedacion', models.CharField(max_length=200, verbose_name='Sedación')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('cooperacion_paciente', models.CharField(max_length=200, verbose_name='Cooperación del Paciente')),
                ('algoritmo_no_intubacion', models.BooleanField(verbose_name='Algoritmo No Intubación')),
                ('crico_tiroidotomia', models.BooleanField(verbose_name='Crico-tiroidotomía')),
                ('traqueostomia_percutanea', models.BooleanField(verbose_name='Traqueostomía Percutánea')),
                ('complicaciones', models.TextField(blank=True, verbose_name='Complicaciones')),
                ('resultado_final', models.TextField(verbose_name='Resultado Final')),
                ('fotos_videos', models.FileField(blank=True, upload_to='fotos_videos_cirugia/', verbose_name='Fotos o Videos Relacionados')),
                ('morbilidad', models.BooleanField(default=False)),
                ('descripcion_morbilidad', models.TextField(blank=True, verbose_name='Descripción Morbilidad')),
                ('mortalidad', models.BooleanField(default=False)),
                ('descripcion_mortalidad', models.TextField(blank=True, verbose_name='Descripción Mortalidad')),
                ('nombre_anestesiologo', models.CharField(max_length=200, verbose_name='Nombre del Anestesiólogo')),
                ('cedula_profesional', models.CharField(max_length=50, verbose_name='Cédula Profesional')),
                ('especialidad', models.CharField(max_length=100, verbose_name='Especialidad')),
                ('nombre_residente', models.CharField(max_length=200, verbose_name='Nombre del Residente')),
            ],
            options={
                'verbose_name': 'Post-During Surgery Form',
                'verbose_name_plural': 'Post-During Surgery Forms',
            },
        ),
    ]
