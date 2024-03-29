# Generated by Django 3.1.2 on 2021-07-16 13:52
import django.db.models.deletion
from django.db import migrations, models
from django.db.transaction import atomic

import archive.models.base
from archive.models import ArchiveFile


@atomic
def move_archive_files(app, schema_editor):
    """
    Convert single file archives to multi-file archives
    """
    archive_instances = (
        list(app.get_model('archive', 'GpxArchive').objects.all())
        + list(app.get_model('archive', 'GoogleTakeoutArchive').objects.all())
        + list(app.get_model('archive', 'JsonArchive').objects.all())
        + list(app.get_model('archive', 'N26CsvArchive').objects.all())
        + list(app.get_model('archive', 'TelegramArchive').objects.all())
        + list(app.get_model('archive', 'TwitterArchive').objects.all())
    )
    for archive_instance in archive_instances:
        ArchiveFile.objects.create(
            archive=archive_instance,
            archive_file=archive_instance.archive_file
        )


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('archive', '0011_facebookarchive'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_key', models.CharField(max_length=50)),
                ('archive_file', models.FileField(upload_to=archive.models.base.archive_path)),
                ('archive_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.RunPython(move_archive_files),
        migrations.RemoveField(
            model_name='googletakeoutarchive',
            name='archive_file',
        ),
        migrations.RemoveField(
            model_name='gpxarchive',
            name='archive_file',
        ),
        migrations.RemoveField(
            model_name='jsonarchive',
            name='archive_file',
        ),
        migrations.RemoveField(
            model_name='n26csvarchive',
            name='archive_file',
        ),
        migrations.RemoveField(
            model_name='telegramarchive',
            name='archive_file',
        ),
        migrations.RemoveField(
            model_name='twitterarchive',
            name='archive_file',
        ),
    ]
