# Generated by Django 4.1.7 on 2023-03-18 16:50

import course_buying.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0012_rename_hastags_course_hashtags'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_issued', models.DateField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt', models.ImageField(upload_to=course_buying.models.get_payment_upload_path)),
                ('status', models.CharField(choices=[('p', 'Pending'), ('a', 'Accepted'), ('r', 'Refused')], default='p', max_length=30)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='course_buying.order')),
            ],
        ),
    ]
