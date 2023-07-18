# Generated by Django 4.2.2 on 2023-07-18 13:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0047_course_state"),
        ("messaging", "0004_alter_messagefile_message"),
    ]

    operations = [
        migrations.RenameField(
            model_name="conversation",
            old_name="teacher",
            new_name="recipient",
        ),
        migrations.AlterField(
            model_name="conversation",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="courses.course",
            ),
        ),
    ]
