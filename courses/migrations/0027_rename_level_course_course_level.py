# Generated by Django 4.1.7 on 2023-05-12 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_course_hashtags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='level',
            new_name='course_level',
        ),
    ]
