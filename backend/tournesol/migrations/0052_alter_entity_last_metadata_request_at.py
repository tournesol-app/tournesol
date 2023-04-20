# Generated by Django 4.1.7 on 2023-04-10 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0051_migrate_ratings_to_its_own_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entity",
            name="last_metadata_request_at",
            field=models.DateTimeField(
                blank=True, help_text="Last time fetch of metadata was attempted", null=True
            ),
        ),
    ]