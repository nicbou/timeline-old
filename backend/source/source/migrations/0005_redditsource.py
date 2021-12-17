# Generated by Django 3.1.2 on 2020-11-03 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0004_twittersource'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedditSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(max_length=50)),
                ('client_secret', models.CharField(max_length=50)),
                ('user_agent', models.CharField(blank=True, max_length=100)),
                ('reddit_username', models.CharField(max_length=20)),
            ],
        ),
    ]