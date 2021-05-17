import json
import os
import uuid

from backend.models import Video
from django_react.settings import SEARCH_YOUTUBE_ENABLE
from backend.run_youtube_dl import 


def search_yt_by_string(s, n=50):
    """Search youtube by string."""
    output = search_on_youtube_playlist(search_phrase=s, n_videos=n)
    return json.loads('[' + ', '.join(output.splitlines()) + ']')


def search_yt_intersect_tournesol(s, n=50, queryset=None):
    """Search youtube, return existing videos in db."""
    if not SEARCH_YOUTUBE_ENABLE:
        return []
    search_result = search_yt_by_string(s=s, n=n)
    videos_yt = [x['id'] for x in search_result]
    if queryset is None:
        queryset = Video.objects.all()
    videos = queryset.filter(video_id__in=videos_yt)
    videos = sorted(videos, key=lambda v: videos_yt.index(v['video_id']))
    return videos
