"""
Function to get twitter account of the uploader of a video.
Used for the Tournesol twitter bot.
"""

import re
from urllib.parse import unquote, urlparse

import requests

from tournesol.utils.api_youtube import get_video_metadata


def get_twitter_handles_from_html(html_text):
    urls = re.findall(r"(https?%3A%2F%2F(?:www\.)?twitter\.com%2F.*?)\"", html_text, re.IGNORECASE)
    handles = []
    for raw_url in urls:
        url = unquote(raw_url)
        handle = urlparse(url).path.strip('/')
        if handle:
            handles.append(handle)
    return handles


def get_twitter_account_from_channel_id(channel_id):
    """Get Twitter account from uploader id"""

    uploader_url = f"https://www.youtube.com/channel/{channel_id}/about"

    resp = requests.get(uploader_url, headers={"user-agent": "curl/7.68.0"}, timeout=10)
    twitter_names = get_twitter_handles_from_html(resp.text)

    if len({name.lower() for name in twitter_names}) == 1:
        return "@" + twitter_names[0]

    print("Error getting the uploader id, Twitter account not found")
    return None


def get_twitter_account_from_video_id(video_id):
    """Get Twitter account from video id"""

    metadata = get_video_metadata(video_id, compute_language=False)
    channel_id = metadata["channel_id"]

    return get_twitter_account_from_channel_id(channel_id)
