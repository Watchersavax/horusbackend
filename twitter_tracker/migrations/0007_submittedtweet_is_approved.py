# Generated by Django 5.1.7 on 2025-03-20 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_tracker', '0006_submittedtweet'),
    ]

    operations = [
        migrations.AddField(
            model_name='submittedtweet',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
