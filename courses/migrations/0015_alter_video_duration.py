# Generated by Django 4.1.7 on 2023-03-26 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_video_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='duration',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]
