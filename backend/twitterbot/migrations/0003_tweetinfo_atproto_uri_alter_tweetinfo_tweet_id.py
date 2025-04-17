# Generated by Django 4.2.11 on 2025-01-27 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("twitterbot", "0002_rename_tweetedvideo_tweetinfo"),
    ]

    operations = [
        migrations.AddField(
            model_name="tweetinfo",
            name="atproto_uri",
            field=models.CharField(
                default=None,
                help_text="URI of the post on the AT protocol network",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tweetinfo",
            name="tweet_id",
            field=models.CharField(
                default=None, help_text="Tweet ID from Twitter URL", max_length=22, null=True
            ),
        ),
    ]
