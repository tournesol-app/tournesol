"""
Post a message in a channel of the Tournesol's Discord server
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from lib.discord.api import publish_on_discord


class Command(BaseCommand):
    help = "Post a message in a Discord channel"

    def add_arguments(self, parser):

        parser.add_argument(
            "-c",
            "--channel",
            type=str,
            help="Name of the channel where the message should be posted",
        )

        parser.add_argument(
            "-m",
            "--message",
            type=str,
            help="Message to post",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        discord_channel = options["channel"]

        if discord_channel not in settings.DISCORD_CHANNEL_WEBHOOKS:
            raise CommandError(
                f"The Discord channel '{discord_channel}' does not exist"
            )

        webhook_url = settings.DISCORD_CHANNEL_WEBHOOKS[discord_channel]

        # display the configuration if more verbosity is asked
        if options.get("verbosity", 1) > 1:
            self.stdout.write(
                f"Discord channel: {discord_channel}\nWebhook: {webhook_url}"
            )

        if publish_on_discord(webhook_url, options["message"]):
            self.stdout.write(
                self.style.SUCCESS(f"Message posted on {discord_channel}")
            )
            self.stdout.write("end")
        else:
            raise CommandError(
                f"Error while posting the message on '{discord_channel}'"
            )
