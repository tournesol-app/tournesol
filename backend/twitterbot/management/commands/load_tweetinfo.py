from pathlib import Path

from django.core.management.base import BaseCommand

from tournesol.entities.video import YOUTUBE_UID_NAMESPACE
from tournesol.models.entity import Entity
from twitterbot.models.tweeted import TweetInfo


class Command(BaseCommand):
    help = "Load already tweeted videos from a file and save data as TweetInfo."

    def add_arguments(self, parser):

        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help=(
                "Relative path to the input file. "
                "Each line must follow the structure {yt_video_id};{BOT_NAME}."
            ),
            required=True,
        )

        # Optional argument
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            default=False,
            help="Dry run, will not alter the database.",
        )

    def handle(self, *args, **options):

        video_to_add_file = Path.cwd() / options["file"]

        if not video_to_add_file.exists():
            raise FileNotFoundError(f"File {video_to_add_file} not found")

        with open(video_to_add_file, "r") as f:

            fake_tweet_id = 10001

            for line in f:
                video_id, bot_name = map(str.strip, line.split(";"))

                if options["dry_run"]:
                    print(video_id, bot_name)
                    continue

                try:
                    video = Entity.objects.get(
                        uid=f"{YOUTUBE_UID_NAMESPACE}:{video_id}"
                    )
                except Entity.DoesNotExist:
                    print(f"Video {video_id} is not in the database")
                    continue

                if TweetInfo.objects.filter(video=video, bot_name=bot_name).exists():
                    print(f"Video {video_id} is already marked as tweeted")
                    continue

                tweet = TweetInfo.objects.create(
                    video=video,
                    tweet_id=str(fake_tweet_id),
                    bot_name=bot_name,
                )

                tweet.datetime_tweet = "2022-01-01T06:00:00Z"
                tweet.save(update_fields=["datetime_tweet"])

                fake_tweet_id += 1
