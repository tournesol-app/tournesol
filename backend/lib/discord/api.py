import requests
import sys


def publish_on_discord(webhook_url, message):
    """Publish a message on a channel of TourneSol Discord server."""

    resp = requests.post(webhook_url, json={"content": message})

    if resp.status_code in [200, 204]:
        return True

    return False
