import requests
import sys
from django.conf import settings

# dummy values just to show the structure, to be replace by settings
DISCORD_CHANNEL_WEBHOOKS = {
    "#test_discord_api": "https://discord.com/api/webhooks/123/xxx-yyy-zzz",
    "#another_discord_channel": "https://discord.com/api/webhooks/123/aaa-bbb-ccc",
}


def publish_on_discord(discord_channel, message):
    """Publish a message on a channel of TourneSol Discord server."""

    webhook_url = DISCORD_CHANNEL_WEBHOOKS[discord_channel]
    resp = requests.post(webhook_url, json={"content": message})

    if resp.status_code in [200, 204]:
        return True

    print(f"Error while publishing on Discord: {resp.status_code}")
    return False


if __name__ == "__main__":

    discord_channel = sys.argv[1]
    message = sys.argv[2]

    if discord_channel not in DISCORD_CHANNEL_WEBHOOKS:
        print(f"Discord channel {discord_channel} not found")
        sys.exit(1)

    publish_on_discord(discord_channel, message)
