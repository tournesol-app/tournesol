# Generated by Django 4.0.6 on 2022-07-18 12:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import tournesol.models.poll


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tournesol", "0042_contributorratingcriteriascore_raw_score_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="ratelater",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="ratelater",
            name="poll",
            field=models.ForeignKey(
                blank=True,
                default=tournesol.models.poll.Poll.default_poll_pk,
                help_text="The poll in which the user is saving the entity.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ratelaters",
                to="tournesol.poll",
            ),
        ),
        migrations.AlterField(
            model_name="ratelater",
            name="datetime_add",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="Time at which the video is saved.",
                null=True,
            ),
        ),
        migrations.RenameField(
            model_name="ratelater", old_name="datetime_add", new_name="created_at"
        ),
        migrations.AlterField(
            model_name="ratelater",
            name="user",
            field=models.ForeignKey(
                help_text="The user who saves the entity.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ratelaters",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="ratelater",
            name="video",
            field=models.ForeignKey(
                help_text="The entity the user wants to save.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ratelaters",
                to="tournesol.entity",
            ),
        ),
        migrations.RenameField(
            model_name="ratelater", old_name="video", new_name="entity"
        ),
        migrations.AlterUniqueTogether(
            name="ratelater",
            unique_together={("poll", "user", "entity")},
        ),
    ]
