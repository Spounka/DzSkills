# Generated by Django 4.1.7 on 2023-06-02 04:35

import admin_dashboard.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_dashboard', '0002_alter_receipt_count_alter_receipt_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template', models.FileField(upload_to=admin_dashboard.models.certificate_upload_dir)),
            ],
        ),
        migrations.CreateModel(
            name='ChosenTeacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='LandingPageImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='TitleScreenText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(default='', max_length=300)),
                ('color', models.CharField(default='#000000', max_length=30, validators=[admin_dashboard.models.validate_color])),
            ],
        ),
        migrations.AddField(
            model_name='adminconfig',
            name='main_title_text',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='main_title', to='admin_dashboard.titlescreentext'),
        ),
        migrations.AddField(
            model_name='adminconfig',
            name='secondary_title_text',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary_title', to='admin_dashboard.titlescreentext'),
        ),
    ]
