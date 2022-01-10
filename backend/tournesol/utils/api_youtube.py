import logging
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_duration
import googleapiclient.discovery

from tournesol.utils.video_language import compute_video_language

logger = logging.getLogger(__name__)

# Get credentials and create an API client
api_service_name = "youtube"
api_version = "v3"

youtube = None
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
if YOUTUBE_API_KEY:
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=YOUTUBE_API_KEY
    )


class VideoNotFound(Exception):
    pass


class YoutubeNotConfiguredError(Exception):
    pass


def get_youtube_video_details(video_id):
    if not youtube:
        raise YoutubeNotConfiguredError(
            "YouTube client not initialized, did you provide an API key?"
        )

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics", id=video_id
    )
    return request.execute()


def get_video_metadata(video_id, compute_language=True):
    try:
        yt_response = get_youtube_video_details(video_id)
    except YoutubeNotConfiguredError:
        return {}
    except Exception:
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
    if compute_language:
        language = compute_video_language(uploader, title, description)
    else:
        language = None
    #  if video has no tags, te field doesn't appear on response
    tags = yt_info["snippet"].get("tags", [])
    duration = parse_duration(yt_info["contentDetails"]["duration"])
    return {
        "name": title,
        "description": description,
        "publication_date": published_date,
        "views": nb_views,
        "uploader": uploader,
        "language": language,
        "tags": tags,
        "duration": duration,
        "metadata_timestamp": timezone.now(),
    }
