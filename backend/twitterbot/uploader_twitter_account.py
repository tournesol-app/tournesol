import re
import requests


def get_uploader_id(video_id):
    """Get YouTube uploader id from YouTube video id"""

    url_video = f"https://www.youtube.com/watch?v={video_id}"

    r = requests.get(url_video)

    if r.status_code != 200:
        raise ConnectionError(f"Error getting video id: {r.status_code}")

    try:
        uploader_id = r.text.split("/channel/")[1].split('"')[0]
    except IndexError:
        return None

    if len(uploader_id) == 24:
        return uploader_id
    else:
        print("Error getting the uploader id, Twitter account not found")
        return None


def get_twitter_account(video_id):
    """Get Twitter account from video id"""

    uploader_id = get_uploader_id(video_id)

    if not uploader_id:
        return None

    uploader_url = f"https://www.youtube.com/channel/{uploader_id}"

    r = requests.get(uploader_url, headers={"user-agent": "curl/7.68.0"})

    twitter_names = re.findall(r"twitter.com\%2F(.*?)\"", r.text)
    twitter_names = [name for name in twitter_names if name != ""]

    if len(set([name.lower() for name in twitter_names])) == 1:
        return "@" + twitter_names[0]
    else:
        print("Error getting the uploader id, Twitter account not found")
        return None
