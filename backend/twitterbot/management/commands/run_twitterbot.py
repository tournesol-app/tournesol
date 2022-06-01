from django.conf import settings
from django.core.management.base import BaseCommand

from twitterbot.tournesolbot import get_video_recommendations, tweet_video_recommendation


class Command(BaseCommand):
    help = "Runs Tournesol Twitter Bot"

    def add_arguments(self, parser):

        parser.add_argument(
            "-n",
            "--bot-name",
            type=str,
            help="Name of the bot '@TournesolBot' or '@TournesolBotFR'",
        )

        # Optional argument
        parser.add_argument(
            "-y",
            "--assumeyes",
            action="store_true",
            default=False,
            help="Answer yes when ask for confirmation. Default: False",
        )

        parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            default=False,
            help="Print the list of tweetable videos.",
        )

    def handle(self, *args, **options):

        bot_name = options["bot_name"]

        if options["list"]:
            language = settings.TWITTERBOT_CREDENTIALS[bot_name]["LANGUAGE"]
            videos = get_video_recommendations(language)

            for video in videos:
                print(
                    video.metadata["video_id"],
                    f"{video.tournesol_score:5.2f}",
                    video.metadata["uploader"],
                    video.metadata["name"],
                    sep=" - ",
                )

            return

        tweet_video_recommendation(bot_name, assumeyes=options["assumeyes"])
