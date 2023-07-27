# Generated by Django 4.2.2 on 2023-07-22 11:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0005_ticket_conversation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="state",
            field=models.CharField(
                choices=[("open", "Open"), ("closed", "Closed")],
                default="open",
                max_length=30,
            ),
        ),
    ]
