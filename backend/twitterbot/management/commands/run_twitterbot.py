from django.core.management.base import BaseCommand

from twitterbot.tournesolbot import tweet_video_recommendation


class Command(BaseCommand):
    help = "Runs Tournesol Twitter Bot"

    def add_arguments(self, parser):

        parser.add_argument(
            "bot_name",
            type=str,
            help="Name of the bot '@TournesolBot' or '@TournesolBotFR'",
        )

        # Optional argument
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            default=False,
            help="Debug mode, will ask for confirmation.",
        )

    def handle(self, *args, **options):

        tweet_video_recommendation(bot_name=options["bot_name"], debug=options["debug"])
