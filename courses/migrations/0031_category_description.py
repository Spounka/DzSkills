# Generated by Django 4.1.7 on 2023-05-21 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0030_category_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.CharField(default='', max_length=300),
        ),
    ]
