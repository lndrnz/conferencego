# Generated by Django 4.0.3 on 2022-07-08 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_location_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='picture_url',
            field=models.URLField(null=True),
        ),
    ]