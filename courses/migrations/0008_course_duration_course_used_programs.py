# Generated by Django 4.1.7 on 2023-03-17 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_course_course_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='duration',
            field=models.CharField(default='1h', max_length=10),
        ),
        migrations.AddField(
            model_name='course',
            name='used_programs',
            field=models.CharField(default='', max_length=300),
        ),
    ]
