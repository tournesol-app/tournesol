from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0019_alter_video_language"),
        ("twitterbot", "0001_initial"),
    ]

    operations = [
        # remove unused fields
        migrations.RemoveField(
            model_name="video",
            name="caption_text",
        ),
        migrations.RemoveField(
            model_name="video",
            name="embedding",
        ),
        migrations.RemoveField(
            model_name="video",
            name="info",
        ),
        migrations.RemoveField(
            model_name="video",
            name="pareto_optimal",
        ),
        migrations.RemoveField(
            model_name="video",
            name="wrong_url",
        ),
        # remove unused models
        migrations.DeleteModel(
            name="VideoRatingThankYou",
        ),
        migrations.DeleteModel(
            name="VideoSelectorSkips",
        ),
        # rename existing models
        migrations.RenameModel("Video", "Entity"),
        migrations.RenameModel("VideoCriteriaScore", "EntityCriteriaScore"),
        migrations.AlterModelOptions(
            name="entity",
            options={"verbose_name_plural": "entities"},
        ),
        # add new entity fields
        migrations.AddField(
            model_name="entity",
            name="metadata",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="entity",
            name="type",
            field=models.CharField(
                choices=[("video", "Video")], max_length=32, null=True
            ),
        ),
        migrations.AddField(
            model_name="entity",
            name="uid",
            field=models.CharField(
                help_text="A unique identifier, build with a namespace and an external id.",
                max_length=144,
                null=True,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="contributorrating",
            name="video",
            field=models.ForeignKey(
                help_text="Entity being scored",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contributorvideoratings",
                to="tournesol.entity",
            ),
        ),
    ]
