# Generated by Django 3.1.2 on 2022-05-16 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0013_icalendararchive'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebookarchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='facebookarchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='googletakeoutarchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='googletakeoutarchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='gpxarchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='gpxarchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='icalendararchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='icalendararchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='jsonarchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='jsonarchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='n26csvarchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='n26csvarchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='telegramarchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='telegramarchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='twitterarchive',
            name='date_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='twitterarchive',
            name='date_until',
            field=models.DateTimeField(null=True),
        ),
    ]
