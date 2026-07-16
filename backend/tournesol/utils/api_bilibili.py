"""
Utilities to fetch video metadata from the Bilibili web API.

Unlike the YouTube API, the Bilibili web API doesn't require an API key.

See https://github.com/SocialSisterYi/bilibili-API-collect for a community
documentation of this API.
"""
import logging
from datetime import datetime, timezone

import requests

from tournesol.utils.api_youtube import VideoNotFound
from tournesol.utils.constants import REQUEST_TIMEOUT
from tournesol.utils.video_language import compute_video_language

logger = logging.getLogger(__name__)

BILIBILI_VIDEO_VIEW_API_URL = "https://api.bilibili.com/x/web-interface/view"

# Error codes returned by the Bilibili API when a video doesn't exist, has
# been deleted, or cannot be accessed.
BILIBILI_VIDEO_NOT_FOUND_CODES = {-400, -404, 62002, 62004, 62012}

# The Bilibili API rejects requests having no usual browser User-Agent.
BILIBILI_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Referer": "https://www.bilibili.com",
}


def get_bilibili_video_details(video_id):
    logger.info("Fetching Bilibili metadata for video_id '%s'", video_id)
    resp = requests.get(
        BILIBILI_VIDEO_VIEW_API_URL,
        params={"bvid": video_id},
        headers=BILIBILI_REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def get_bilibili_video_metadata(video_id, compute_language=True):
    try:
        response = get_bilibili_video_details(video_id)
    except Exception:  # pylint: disable=broad-except
        logger.error(
            "Failed to retrieve video metadata from Bilibili for video_id '%s'",
            video_id,
            exc_info=True,
        )
        return {}

    if response.get("code") != 0:
        if response.get("code") in BILIBILI_VIDEO_NOT_FOUND_CODES:
            raise VideoNotFound

        logger.error(
            "Unexpected error code %s from the Bilibili API for video_id '%s': %s",
            response.get("code"),
            video_id,
            response.get("message"),
        )
        return {}

    data = response["data"]
    title = data.get("title", "")
    description = data.get("desc", "")
    uploader = data.get("owner", {}).get("name", "")
    channel_id = data.get("owner", {}).get("mid")
    publication_timestamp = data.get("pubdate")

    if compute_language:
        language = compute_video_language(uploader, title, description)
    else:
        language = None

    return {
        "source": "bilibili",
        "name": title,
        "description": description,
        "publication_date": (
            datetime.fromtimestamp(publication_timestamp, tz=timezone.utc).isoformat()
            if publication_timestamp is not None
            else None
        ),
        "views": data.get("stat", {}).get("view"),
        "uploader": uploader,
        "channel_id": str(channel_id) if channel_id is not None else None,
        "language": language,
        # The Bilibili API exposes no tags in this endpoint.
        "tags": [],
        "duration": data.get("duration"),
        # Bilibili has no equivalent of the YouTube unlisted status.
        "is_unlisted": False,
        # Unlike YouTube thumbnails, Bilibili thumbnail URLs cannot be
        # derived from the video id, so they must be stored.
        "thumbnail_url": data.get("pic"),
    }
