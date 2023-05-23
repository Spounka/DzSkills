# Generated by Django 4.1.7 on 2023-05-22 19:11

import admin_dashboard.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='count',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='image',
            field=models.FileField(upload_to=admin_dashboard.models.receipt_upload_dir),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='is_current',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
