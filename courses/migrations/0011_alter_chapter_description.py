# Generated by Django 4.1.7 on 2023-03-18 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_alter_course_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='description',
            field=models.CharField(max_length=300),
        ),
    ]
