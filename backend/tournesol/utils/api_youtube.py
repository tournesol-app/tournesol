import logging

import googleapiclient.discovery
from django.conf import settings
from django.utils.dateparse import parse_duration

from tournesol.utils.video_language import compute_video_language

logger = logging.getLogger(__name__)

# Get credentials and create an API client
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

YOUTUBE = None
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
if YOUTUBE_API_KEY:
    YOUTUBE = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, developerKey=YOUTUBE_API_KEY
    )


class VideoNotFound(Exception):
    pass


class YoutubeNotConfiguredError(Exception):
    pass


def get_youtube_video_details(video_id):
    if not YOUTUBE:
        raise YoutubeNotConfiguredError(
            "YouTube client not initialized, did you provide an API key?"
        )

    # pylint: disable=no-member
    request = YOUTUBE.videos().list(
        part="snippet,contentDetails,statistics,status", id=video_id
    )
    return request.execute()


def get_video_metadata(video_id, compute_language=True):
    try:
        yt_response = get_youtube_video_details(video_id)
    except YoutubeNotConfiguredError:
        return {}
    except Exception:  # pylint: disable=broad-except
        logger.error("Failed to retrieve video metadata from Youtube", exc_info=True)
        return {}

    yt_items = yt_response.get("items", [])
    if len(yt_items) == 0:
        raise VideoNotFound

    yt_info = yt_items[0]
    title = yt_info["snippet"]["title"]
    nb_views = yt_info.get("statistics", {}).get("viewCount")
    published_date = str(yt_info["snippet"]["publishedAt"])
    published_date = published_date.split("T")[0]
    # we could truncate description to spare some space
    description = str(yt_info["snippet"]["description"])
    uploader = yt_info["snippet"]["channelTitle"]
    channel_id = yt_info["snippet"]["channelId"]
    if compute_language:
        language = compute_video_language(uploader, title, description)
    else:
        language = None
    #  if video has no tags, the field doesn't appear on response
    tags = yt_info["snippet"].get("tags", [])
    duration = parse_duration(yt_info["contentDetails"]["duration"])
    is_unlisted = yt_info["status"].get("privacyStatus") == "unlisted"
    return {
        "source": "youtube",
        "name": title,
        "description": description,
        "publication_date": published_date,
        "views": nb_views,
        "uploader": uploader,
        "channel_id": channel_id,
        "language": language,
        "tags": tags,
        "duration": int(duration.total_seconds()) if duration else None,
        "is_unlisted": is_unlisted,
    }
