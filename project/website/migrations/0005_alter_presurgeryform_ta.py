# Generated by Django 5.1.2 on 2024-11-05 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_alter_presurgeryform_imc_alter_presurgeryform_peso_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presurgeryform',
            name='ta',
            field=models.TextField(verbose_name='TA'),
        ),
    ]
