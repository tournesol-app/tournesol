import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from solidago.pipeline.inputs import TournesolDataset

from core.models import User
from core.models.user import EmailDomain
from tournesol.models import Comparison, ComparisonCriteriaScore, ContributorRating, Entity, Poll
from tournesol.models.poll import ALGORITHM_MEHESTAN

PUBLIC_DATASET_URL = "https://api.tournesol.app/exports/all/"
RANDOM_SEED = 0
SEED_USERS = ["aidjango", "le_science4all", "lpfaucon", "biscuissec", "amatissart"]

thread_pool = ThreadPoolExecutor(max_workers=10)


class Command(BaseCommand):
    help = "Generate a new database for dev purposes, derived from the public dataset"

    def add_arguments(self, parser):
        parser.add_argument("--dataset-url", type=str, default=PUBLIC_DATASET_URL)
        sampling_group = parser.add_mutually_exclusive_group()
        sampling_group.add_argument("--user-sampling", type=float, default=None)
        sampling_group.add_argument("--videos-limit", type=int, default=None)

    def create_user(self, username: str, ml_input: TournesolDataset):
        user = ml_input.users.loc[ml_input.users.public_username == username].iloc[0]
        is_pretrusted = user.trust_score > 0.5
        email = f"{username}@trusted.example" if is_pretrusted else f"{username}@example.com"
        user = User.objects.create_user(
            username=username,
            email=email,
            is_staff=username in SEED_USERS,
            trust_score=user.trust_score,
        )
        if user.is_staff:
            # Set a default password for staff accounts (used in e2e tests, etc.)
            user.set_password("tournesol")
            user.save()
        return user

    def create_videos(self, video_ids: pd.Series) -> dict[int, Entity]:
        videos = {}
        for entity_id, video_id in video_ids.items():
            videos[entity_id] = Entity.create_from_video_id(video_id, fetch_metadata=False)
        return videos

    def fetch_video_metadata(self, videos):
        def refresh_metadata(video):
            video.inner.refresh_metadata(force=True, compute_language=True)

        futures = (thread_pool.submit(refresh_metadata, video) for video in videos.values())
        for future in concurrent.futures.as_completed(futures):
            # .result() will reraise any exception occurred during refresh
            future.result()

        thread_pool.shutdown()

    def create_test_user(self):
        User.objects.create_user(  # hardcoded password is deliberate # nosec B106
            username="user1", password="tournesol", email="user1@tournesol.app"
        )

    @staticmethod
    def apply_videos_limit(limit: int, comparisons: pd.DataFrame):
        counts_a = (
            comparisons.drop_duplicates(
                subset=["entity_a", "public_username"], keep="first", inplace=False
            )
            .entity_a.value_counts()
            .rename("count_a")
        )
        counts_b = (
            comparisons.drop_duplicates(
                subset=["entity_b", "public_username"], keep="first", inplace=False
            )
            .entity_b.value_counts()
            .rename("count_b")
        )
        counts_combined = pd.concat([counts_a, counts_b], axis=1).fillna(0)
        counts_combined["total_count"] = counts_combined.count_a + counts_combined.count_b
        videos_to_keep = set(
            counts_combined.sort_values(by="total_count", ascending=False).index[:limit]
        )
        comparisons = comparisons[
            comparisons.entity_a.isin(videos_to_keep) & comparisons.entity_b.isin(videos_to_keep)
        ]
        usernames_to_keep = comparisons.public_username.unique()
        print(
            f"Applied video limits: \n"
            f"- New video count: {len(videos_to_keep)}\n"
            f"- New user count: {len(usernames_to_keep)}\n"
            f"- New comparison count: {len(comparisons)}"
        )
        return usernames_to_keep, videos_to_keep, comparisons

    def handle(self, *args, **options):
        public_dataset = TournesolDataset(options["dataset_url"])
        nb_comparisons = 0

        with transaction.atomic():
            poll = Poll.default_poll()
            poll.algorithm = ALGORITHM_MEHESTAN
            poll.save()

            usernames = public_dataset.users.public_username.unique()
            comparisons = public_dataset.comparisons
            video_ids = public_dataset.entity_id_to_video_id

            if options["user_sampling"]:
                usernames = set(
                    pd.Series(usernames)
                    .sample(frac=options["user_sampling"], random_state=RANDOM_SEED)
                    .values
                ).union(SEED_USERS)
                comparisons = comparisons[comparisons.public_username.isin(usernames)]
                video_ids = video_ids[
                    video_ids.index.isin(set(comparisons.entity_a) | set(comparisons.entity_b))
                ]

            if options["videos_limit"]:
                usernames, entity_ids, comparisons = self.apply_videos_limit(
                    options["videos_limit"], comparisons
                )
                video_ids = video_ids[video_ids.index.isin(entity_ids)]

            EmailDomain.objects.create(
                domain="@trusted.example", status=EmailDomain.STATUS_ACCEPTED
            )
            users = {
                username: self.create_user(username, public_dataset) for username in usernames
            }
            print(f"Created {len(users)} users")

            videos = self.create_videos(video_ids=video_ids)
            print(f"Created {len(videos)} video entities")

            for (username, entity_a, entity_b), rows in comparisons.groupby(
                ["public_username", "entity_a", "entity_b"]
            ):
                comparison = Comparison.objects.create(
                    user=users[username],
                    poll=poll,
                    entity_1=videos[entity_a],
                    entity_2=videos[entity_b],
                )
                for values in rows.itertuples(index=False):
                    ComparisonCriteriaScore.objects.create(
                        comparison=comparison,
                        criteria=values.criterion,
                        score=values.score,
                        score_max=values.score_max,
                    )
                nb_comparisons += 1
            print(f"Created {nb_comparisons} comparisons")

            for video in videos.values():
                video.update_entity_poll_rating(poll=poll)

            self.create_test_user()
            ContributorRating.objects.update(is_public=True, entity_seen=True)

        if settings.YOUTUBE_API_KEY:
            print("Fetching video metadata from Youtube...")
            self.fetch_video_metadata(videos)
            print("Done.")

        print("Running ml-train...")
        call_command("ml_train", "--no-trust-algo")
