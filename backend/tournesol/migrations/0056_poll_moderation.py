# Generated by Django 4.2.7 on 2023-11-15 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0055_alter_criterialocale_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="moderation",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
