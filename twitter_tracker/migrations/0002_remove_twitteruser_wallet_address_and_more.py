# Generated by Django 5.1.7 on 2025-03-16 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_tracker', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twitteruser',
            name='wallet_address',
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='profile_image',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='twitter_handle',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
