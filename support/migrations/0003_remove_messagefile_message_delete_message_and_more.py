# Generated by Django 4.2.2 on 2023-07-18 14:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0002_remove_ticket_user_delete_report"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="messagefile",
            name="message",
        ),
        migrations.DeleteModel(
            name="Message",
        ),
        migrations.DeleteModel(
            name="MessageFile",
        ),
    ]
