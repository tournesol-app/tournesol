#!/usr/bin/env python

import discord
import re
import os
import requests

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

yt_url_re = re.compile(r"\b(?:https?:)?(?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed|live)(?:\.php)?(?:\?\S*v=|\/))([a-zA-Z0-9\_-]{11})(?:[\?&][a-zA-Z0-9\_-]+=[a-zA-Z0-9\_-]+)*(?:[&\/\#].*)?\b")


token = os.environ["DISCORD_BOT_TOKEN"]
tournesol_api_url = os.environ["TOURNESOL_API_URL"]


def video_exists(video_id: str) -> bool:
    resp = requests.head(f"{tournesol_api_url}/video/{video_id}/")
    if resp.status_code != requests.codes.ok:
        print(f"video {video_id} not found in Tournesol")
        return False
    print(f"video {video_id} found in Tournesol")
    return True


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    url_matches = set(yt_url_re.findall(message.content))
    if len(url_matches) > 0:
        print(f'Found a message containing video ids: {", ".join(url_matches)}')
        links = [f"https://tournesol.app/entities/yt:{video_id}" for video_id in url_matches if video_exists(video_id)]
        if len(links) > 0:
            msg = f"Please use Tournesol links when posting on social media to help us promote the project:\n" + "\n".join(links)
        # if message.content:
            await message.channel.send(msg)


client.run(token)
