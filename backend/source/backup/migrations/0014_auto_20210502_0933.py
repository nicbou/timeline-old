# Generated by Django 3.1.2 on 2021-05-02 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0013_auto_20210419_1110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='filesystemsource',
            options={'ordering': ['key']},
        ),
        migrations.AlterModelOptions(
            name='hackernewssource',
            options={'ordering': ['key']},
        ),
        migrations.AlterModelOptions(
            name='redditsource',
            options={'ordering': ['key']},
        ),
        migrations.AlterModelOptions(
            name='rsssource',
            options={'ordering': ['key']},
        ),
        migrations.AlterModelOptions(
            name='twittersource',
            options={'ordering': ['key']},
        ),
        migrations.AddField(
            model_name='filesystemsource',
            name='key',
            field=models.SlugField(max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='hackernewssource',
            name='key',
            field=models.SlugField(max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='redditsource',
            name='key',
            field=models.SlugField(max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='rsssource',
            name='key',
            field=models.SlugField(max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='twittersource',
            name='key',
            field=models.SlugField(max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='rsyncdestination',
            name='key',
            field=models.SlugField(max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='rsyncsource',
            name='key',
            field=models.SlugField(max_length=80, null=True),
        ),
    ]