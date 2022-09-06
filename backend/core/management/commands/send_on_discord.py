"""
Send a message to a configured Discord channel.

The web hook of the target channel must be configured in the settings.
"""

from django.core.management.base import BaseCommand

from core.lib.discord.api import write_in_channel


class Command(BaseCommand):
    help = "Send a message to a configured Discord channel."

    def add_arguments(self, parser):

        parser.add_argument(
            "-c",
            "--channel",
            type=str,
            help="Name of the target channel.",
        )

        parser.add_argument(
            "-m",
            "--message",
            type=str,
            help="Message to send.",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")
        discord_channel = options["channel"]

        # display the configuration if more verbosity is asked
        if options.get("verbosity", 1) > 1:
            self.stdout.write(f"Discord channel: {discord_channel}")

        write_in_channel(discord_channel, options["message"])

        self.stdout.write(self.style.SUCCESS(f"Message posted on {discord_channel}"))
        self.stdout.write("end")
