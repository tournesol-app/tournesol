# Generated by Django 4.2.7 on 2023-12-04 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0057_entitycontext_entitycontextlocale"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="poll",
            name="moderation",
        ),
    ]
