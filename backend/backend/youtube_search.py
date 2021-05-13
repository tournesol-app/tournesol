import json
import os
import uuid

from backend.models import Video
from django_react.settings import SEARCH_YOUTUBE_ENABLE


def search_yt_by_string(s, n=50):
    """Search youtube by string."""
    
    # Sergei, 13th May 2021
    # Disabled until #100 is fixed
    # TODO: re-enable
    
    return []
    
    # s = json.dumps(s)[1:-1]
    s = s.replace('"', '\"')
    path = str(uuid.uuid1()) + '.json'
    os.system(
        'youtube-dl --flat-playlist --skip-download --print-json ytsearch%d:"%s" > %s' %
        (n, s, path))
    s = open(path, 'r').read()
    os.unlink(path)

    return json.loads('[' + ', '.join(s.splitlines()) + ']')


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
