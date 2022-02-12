import re
import requests
from tournesol.utils.api_youtube import get_video_metadata


def get_twitter_account(video_id):
    """Get Twitter account from video id"""

    metadata = get_video_metadata(video_id, compute_language=False)
    uploader_id = metadata["uploader_id"]
    uploader_url = f"https://www.youtube.com/channel/{uploader_id}"

    r = requests.get(uploader_url, headers={"user-agent": "curl/7.68.0"})

    twitter_names = re.findall(r"twitter.com\%2F(.*?)\"", r.text)
    twitter_names = [name for name in twitter_names if name != ""]

    if len(set(name.lower() for name in twitter_names)) == 1:
        return "@" + twitter_names[0]
    else:
        print("Error getting the uploader id, Twitter account not found")
        return None
