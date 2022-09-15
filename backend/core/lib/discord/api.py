import logging

import requests
from django.conf import settings


def write_in_channel(discord_channel, message) -> bool:
    """Write a message in a Discord channel."""
    webhook_url = settings.DISCORD_CHANNEL_WEBHOOKS.get(discord_channel, "")

    if not webhook_url:
        logging.warning("Cannot write in discord channel %s", discord_channel)
        logging.warning("Cause: empty webhook URL.")
        return False

    resp = requests.post(webhook_url, json={"content": message})
    resp.raise_for_status()
    return True
