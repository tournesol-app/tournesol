import requests
import sys
from django.conf import settings

# dummy values just to show the structure, to be replace by settings
DISCORD_CHANNEL_WEBHOOKS = {
    "#test_discord_api": "https://discord.com/api/webhooks/123/xxx-yyy-zzz",
    "#another_discord_channel": "https://discord.com/api/webhooks/123/aaa-bbb-ccc",
}


def publish_on_discord(webhook_url, message):
    """Publish a message on a channel of TourneSol Discord server."""

    resp = requests.post(webhook_url, json={"content": message})

    if resp.status_code in [200, 204]:
        return True

    return False
