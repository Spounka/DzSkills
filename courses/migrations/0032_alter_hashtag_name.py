# Generated by Django 4.1.7 on 2023-05-23 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_category_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='name',
            field=models.CharField(default='', max_length=20),
        ),
    ]
