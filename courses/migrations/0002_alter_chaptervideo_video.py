# Generated by Django 4.1.7 on 2023-03-03 20:05

import courses.models
from django.db import migrations, models

import courses.upload_paths


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chaptervideo',
            name='video',
            field=models.FileField(upload_to=courses.upload_paths.get_video_upload_directory),
        ),
    ]
