# Generated by Django 4.2.7 on 2023-12-14 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0059_remove_poll_moderation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="entity",
            name="tournesol_score",
        ),
    ]
