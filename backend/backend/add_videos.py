import datetime
# for video descriptions
import json
import os
import gin
# for sleep
import time
from django.utils.timezone import make_aware
import numpy as np
# launch with Django -- via manage.py (see global README)
from backend.models import Video
from langdetect import detect
from path import Path
from tqdm.auto import tqdm
from django_react.settings import BASE_DIR
import logging
from django.db import transaction
from time import sleep
from django_react.settings import load_gin_config
import threading
from backend.run_youtube_dl import download_video_info


def load_videos_thread(config):
    """Download metadata for a few videos."""
    to_download = qs_videos_to_download()

    to_download_subsample = qs_subsample_to_download(to_download)
    ids = [x.video_id for x in to_download_subsample]

    if not ids:
        print("No videos, exiting!")
        return

    print(f"Total to-download: {to_download.count()} subsampled: {len(ids)}")

    load_gin_config(config)
    vm = VideoManager(only_download=ids)
    vm.fill_info()
    vm.add_videos_in_folder_to_db()
    vm.clear_info()


@gin.configurable
def video_thread_timeout(config, max_time_sec=60.0):
    """Get data from youtube, run periodically."""
    x = threading.Thread(target=load_videos_thread, args=(config,))
    x.start()
    t0 = time.time()

    while time.time() - t0 <= max_time_sec:
        if not x.is_alive():
            print("Finished OK")
            x.join()
            return True

    print("Timeout reached")
    return False


@gin.configurable
def qs_videos_to_download(base_qs=None, max_download_times=5):
    """Get a list of videos to download, see #321."""

    if base_qs is None:
        base_qs = Video.objects.all()

    # initial queryset
    qs = base_qs

    # removing ones with name set
    qs = qs.exclude(publication_date__isnull=False)

    # removing videos that are wrong for sure
    qs = qs.exclude(wrong_url=True)

    # remove videos which are unlisted
    qs = qs.exclude(is_unlisted=True)

    # removing already downloaded videos
    qs = qs.exclude(metadata_timestamp__isnull=False)

    # removing ones with too many (unsuccessful) attempts
    qs = qs.exclude(download_attempts__gt=max_download_times)

    # sorting by addition date (load the most recent ones first)
    qs = qs.order_by('download_attempts', '-add_time')

    return qs


@gin.configurable
def qs_subsample_to_download(qs, limit=10, max_output=3):
    """Select first :limit, then randomly sample max_output from those."""
    qs = list(qs[:limit])

    if len(qs) > max_output:
        idxes = np.random.choice(len(qs), max_output, replace=False)
    else:
        idxes = range(len(qs))

    return [qs[i] for i in idxes]


def language_for_video(v):
    """Get language for a video using langdetect."""
    t = [v.name, v.description]
    t = [s for s in t if s and s.strip()]
    t = ' '.join(t)
    if not t:
        return ''
    return detect(t)


def video_fill_info(v):
    """Fill details for a video."""
    if v.info is None:
        return

    # converting data
    info = v.info  # ast.literal_eval(v.info)

    date = datetime.datetime.strptime(info['upload_date'], '%Y%m%d')
    date = date.strftime('%Y-%m-%d')
    duration = datetime.timedelta(seconds=info['duration'])

    # saving data
    v.duration = duration
    v.language = language_for_video(v)
    v.publication_date = date
    v.views = info['view_count']
    v.uploader = info['uploader']

    v.metadata_timestamp = make_aware(datetime.datetime.now())
    v.save()


def time_convert_secs_to_hms_string(secs):
    """Convert seconds (int) to H:M:S."""
    duration_hms = int(secs)
    duration_h = duration_hms // 3600
    duration_ms = duration_hms - duration_h * 3600
    duration_m = duration_ms // 60
    duration_s = duration_ms - duration_m * 60

    duration = "%02d:%02d:%02d" % (duration_h, duration_m, duration_s)
    return duration


@gin.configurable
class VideoManager(object):
    """Adds video from search -> ytdl -> db."""

    def __init__(self, video_dir, only_download=None,
                 after_download_delay_sec=1):
        # using paths relative to the BASE_DIR
        if not video_dir.startswith('.'):
            video_dir = os.path.join(BASE_DIR, video_dir)

        self.video_dir = video_dir
        self.after_download_delay_sec = after_download_delay_sec
        self.only_download = set(only_download) if isinstance(only_download, list) else None

        self.ids_in_folder = []
        self.upload_ids = []

        os.makedirs(self.video_dir, exist_ok=True)
        self.last_fill_info = None
        self.only_download_to_db()

    def search_videos(self, NUM_VIDEOS=100,
                      SEARCH_PHRASE="covid-19"):
        """Search for videos and save their metadata to a folder."""
        with Path(self.video_dir):
            raise NotImplementedError("Search on youtube for adding videos is disabled"
                                      ", use the Rate Later list!")

    def get_queryset(self):
        """All videos or only_download videos."""
        qs = Video.objects.all()
        qs = qs.filter(wrong_url=False)
        if self.only_download:
            qs = qs.filter(video_id__in=list(self.only_download))
        return qs

    def only_download_to_db(self):
        """Create videos from the only_download list."""
        if not self.only_download:
            return None
        return Video.objects.bulk_create(
                [Video(video_id=vid)
                 for vid in self.only_download],
                ignore_conflicts=True)

    def fill_info(self):
        """Given a list of videos, download their metadata."""
        ret_text = {}

        with Path(self.video_dir):
            os.system('rm -- *.info.json *.description *.dump')
            videos = self.get_queryset()
            for v in tqdm(videos):
                vid = v.video_id
                if self.only_download and vid not in self.only_download:
                    continue
                out = download_video_info(str(vid))
                ret_text[vid] = out
                sleep(self.after_download_delay_sec)
        self.last_fill_info = ret_text
        return ret_text

    def add_videos_in_folder_to_db(self):
        """Take videos from folder and load meta-data to db."""
        with Path(self.video_dir):

            # list of video IDs
            suffix = '.description'

            self.ids_in_folder = [x[:-len(suffix)]
                                  for x in os.listdir() if x.endswith(suffix)]

            ids_in_folder_set = set(self.ids_in_folder)

            # list of .dump files for a particular video ID
            self.dump_files = {
                id_in_folder: [x for x in os.listdir() if x.startswith(id_in_folder)
                               and x.endswith('.dump')]
                for id_in_folder in self.ids_in_folder
            }

            # is video unlisted? might break if youtube changes
            UNLISTED_STR_HTML = '<meta itemprop="unlisted" content="True">'
            is_unlisted = {
                video_id: any([UNLISTED_STR_HTML in open(dump, 'r').read()
                               for dump in dumps])
                for video_id, dumps in self.dump_files.items()
            }

            # adding video IDs in case if they don't exist
            Video.objects.bulk_create([
                    Video(video_id=vid)
                    for vid in self.ids_in_folder
                ], ignore_conflicts=True)

            for video_ in self.get_queryset():
                wrong_url = 'is not a valid URL' in self.last_fill_info[video_.video_id]

                with transaction.atomic():
                    video = Video.objects.get(pk=video_.pk)
                    video.wrong_url = wrong_url
                    video.download_failed = video.video_id not in ids_in_folder_set
                    video.is_unlisted = is_unlisted.get(video.video_id, False)
                    video.last_download_time = make_aware(datetime.datetime.now())
                    video.download_attempts += 1
                    video.save()

                if video.wrong_url:
                    logging.warning(f"Video {video.video_id} has a wrong url")
                if video.download_failed:
                    logging.warning(f"Metadata download for {video.video_id} failed")
                if video.is_unlisted:
                    logging.warning(f"Video {video.video_id} is unlisted")

            # saving descriptions and info
            for v in tqdm(self.get_queryset()):
                vid = v.video_id
                if vid not in self.ids_in_folder:
                    continue

                info = json.load(open('%s.info.json' % vid, 'r'))
                description = open('%s.description' % vid, 'r').read()

                v.description = description
                v.name = info['title']
                v.info = info
                v.save()

                try:
                    video_fill_info(v)
                except Exception:
                    print("Info fill failure for %s" % vid)

    def clear_info(self):
        """Remove .info field for all videos."""
        Video.objects.all().update(info="")
