# Generated by Django 3.1.2 on 2021-03-16 13:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0008_auto_20210127_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsyncsource',
            name='max_backups',
            field=models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='rsyncsource',
            name='port',
            field=models.PositiveIntegerField(default=22, validators=[django.core.validators.MaxValueValidator(65535)]),
        ),
    ]
