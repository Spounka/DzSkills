# Generated by Django 4.2.2 on 2023-07-20 21:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0048_studentprogress_disabled_alter_studentprogress_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="studentprogress",
            name="progress_percentage",
        ),
        migrations.AlterField(
            model_name="studentprogress",
            name="disabled",
            field=models.BooleanField(default=False),
        ),
    ]
