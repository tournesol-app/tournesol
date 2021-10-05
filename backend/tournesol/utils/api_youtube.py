# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import googleapiclient.discovery
from settings.settings import YOUTUBE_API_KEY

# Get credentials and create an API client
api_service_name = "youtube"
api_version = "v3"

youtube = None
if YOUTUBE_API_KEY:
    youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=YOUTUBE_API_KEY)


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def youtube_video_details(video_id):
    if not youtube:
        raise AssertionError('YouTube client not initialized, did you provide an API key?')

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    return (response)
