# Generated by Django 4.1.7 on 2023-05-31 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0035_alter_coursequizz_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizzquestion',
            name='is_correct_answer',
        ),
        migrations.CreateModel(
            name='QuizzAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(default='', max_length=200)),
                ('is_correct_answer', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='courses.quizzquestion')),
            ],
        ),
    ]
