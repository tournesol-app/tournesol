import random
import concurrent
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction

from core.models import User
from tournesol.models import Comparison, Poll
from tournesol.models.comparisons import ComparisonCriteriaScore
from tournesol.models.entity import Entity
from tournesol.models.poll import ALGORITHM_MEHESTAN

PUBLIC_DATASET_URL = "https://api.tournesol.app/exports/comparisons/"
RANDOM_SEED = 0

thread_pool = ThreadPoolExecutor(max_workers=10)

class Command(BaseCommand):
    help = "Generate a new database for dev purposes, derived from the public dataset"

    def add_arguments(self, parser):
        parser.add_argument('--user-sampling', type=float, default=None)

    def create_user(self, username):
        # TODO assign trusted or not-trusted address at random
        return User.objects.create_user(username=username, email=f"{username}@example.com")

    def create_videos(self, video_ids):
        videos = {}
        for video_id in video_ids:
            videos[video_id] = Entity.create_from_video_id(video_id, fetch_metadata=False)
        return videos

    def fetch_video_metadata(self, videos):
        def refresh_metadata(video):
            video.inner.refresh_metadata(force=True, compute_language=True)

        futures = (thread_pool.submit(refresh_metadata, video) for video in videos.values())
        for future in concurrent.futures.as_completed(futures):
            # .result() will reraise any exception occured during refresh
            future.result()


    def handle(self, *args, **options):
        random.seed(RANDOM_SEED)

        public_dataset = pd.read_csv(PUBLIC_DATASET_URL)
        nb_comparisons = 0

        with transaction.atomic():
            poll = Poll.default_poll()
            poll.algorithm = ALGORITHM_MEHESTAN
            poll.save()

            usernames = public_dataset.public_username.unique()
            if options["user_sampling"]:
                usernames = pd.Series(usernames).sample(frac=options["user_sampling"], random_state=RANDOM_SEED).values
                public_dataset = public_dataset[public_dataset.public_username.isin(usernames)]

            users = {
                username: self.create_user(username)
                for username in usernames
            }
            print(f"Created {len(users)} users")

            videos = self.create_videos(set(public_dataset.video_a) | set(public_dataset.video_b))
            print(f"Created {len(videos)} video entities")

            for ((username, video_a, video_b), rows) in public_dataset.groupby(
                ["public_username", "video_a", "video_b"]
            ):
                comparison = Comparison.objects.create(
                    user=users[username],
                    poll=poll,
                    entity_1=videos[video_a],
                    entity_2=videos[video_b],
                )
                for _, values in rows.iterrows():
                    ComparisonCriteriaScore.objects.create(
                        comparison=comparison,
                        criteria=values["criteria"],
                        score=values["score"],
                        weight=values["weight"],
                    )
                nb_comparisons += 1
            print(f"Created {nb_comparisons} comparisons")

            print(f"Computing n_ratings...")
            for entity in Entity.objects.iterator():
                entity.update_n_ratings()
            print(f"Done.")

        if settings.YOUTUBE_API_KEY:
            print("Fetching video metadata from Youtube...")
            self.fetch_video_metadata(videos)
            print("Done.")
        
        print("Running ml-train...")
        call_command("ml_train")
