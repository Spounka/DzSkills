# Generated by Django 4.1.7 on 2023-03-16 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_course_trending'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_level',
            field=models.CharField(choices=[('beg', 'Beginner'), ('interm', 'Intermediate'), ('advanced', 'Advanced')], default='beg', max_length=30),
        ),
    ]
