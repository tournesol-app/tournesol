import logging

import requests


def write_in_channel(webhook_url, discord_channel, message) -> bool:
    """Write a message in a Discord channel."""
    if not webhook_url:
        logging.warning("Cannot write in discord channel %s", discord_channel)
        logging.warning("Cause: empty webhook URL.")
        return False

    resp = requests.post(webhook_url, json={"content": message})
    resp.raise_for_status()
    return True
