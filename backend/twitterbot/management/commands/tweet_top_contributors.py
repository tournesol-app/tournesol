from django.core.management.base import BaseCommand

from twitterbot.tournesolbot import tweet_top_contributor_graph


class Command(BaseCommand):
    help = "Runs Tournesol Twitter Bot to tweet Top contributor figure"

    def add_arguments(self, parser):

        parser.add_argument(
            "-n",
            "--bot-name",
            type=str,
            required=True,
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

    def handle(self, *args, **options):

        tweet_top_contributor_graph(options["bot_name"], assumeyes=options["assumeyes"])
