# Generated by Django 4.2.11 on 2024-04-08 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0060_remove_entity_tournesol_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="comparisoncriteriascore",
            name="score_magnitude",
            field=models.IntegerField(
                default=10.0, help_text="The absolute value of the maximum score."
            ),
        ),
    ]
