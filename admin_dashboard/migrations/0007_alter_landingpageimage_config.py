# Generated by Django 4.1.7 on 2023-06-02 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_dashboard', '0006_landingpageimage_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpageimage',
            name='config',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='admin_dashboard.adminconfig'),
        ),
    ]
