# Generated by Django 4.2.2 on 2023-07-23 08:48

import admin_dashboard.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admin_dashboard", "0007_alter_landingpageimage_config"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ChosenTeacher",
        ),
        migrations.AlterField(
            model_name="landingpageimage",
            name="image",
            field=models.FileField(
                upload_to=admin_dashboard.models.landing_page_upload_dir
            ),
        ),
    ]
