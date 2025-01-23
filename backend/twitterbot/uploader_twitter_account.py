"""
Function to get twitter account of the uploader of a video.
Used for the Tournesol twitter bot.
"""

import re
from urllib.parse import unquote, urlparse

import requests

from tournesol.utils.api_youtube import get_video_metadata


def get_video_channel_html(video_id: str):
    metadata = get_video_metadata(video_id, compute_language=False)
    channel_id = metadata["channel_id"]
    channel_about_url = f"https://www.youtube.com/channel/{channel_id}/about"
    resp = requests.get(channel_about_url, headers={"user-agent": "curl/7.68.0"}, timeout=10)
    resp.raise_for_status()
    return resp.text


def get_twitter_handles_from_html(html_text):
    urls = re.findall(r"(https?%3A%2F%2F(?:www\.)?twitter\.com%2F.*?)\"", html_text, re.IGNORECASE)
    handles: set[str] = set()
    for raw_url in urls:
        url = unquote(raw_url)
        handle = urlparse(url).path.strip("/")
        if handle:
            handles.add(f"@{handle.lower()}")
    return handles


def get_twitter_account_from_video_id(video_id: str):
    """Get Twitter account from video id"""

    channel_html = get_video_channel_html(video_id)
    handles = get_twitter_handles_from_html(channel_html)

    if len(handles) == 1:
        return handles.pop()

    if len(handles) > 1:
        print("Error getting the uploader han, Twitter account not found")

    if len(handles) == 0:
        print("Twitter account not found: no handle found in html.")

    return None
