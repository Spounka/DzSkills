# Generated by Django 4.1.7 on 2023-03-18 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_alter_chapter_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='hastags',
            new_name='hashtags',
        ),
    ]
