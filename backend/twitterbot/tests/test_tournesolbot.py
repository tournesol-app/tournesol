from datetime import timedelta
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone

from core.tests.factories.user import UserFactory
from core.utils.time import time_ago
from tournesol.models import Entity, EntityPollRating, Poll
from tournesol.models.comparisons import Comparison
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import EntityFactory, VideoCriteriaScoreFactory, VideoFactory
from tournesol.tests.factories.ratings import ContributorRatingFactory
from tournesol.utils.contributors import get_top_public_contributors_last_month
from twitterbot.tournesolbot import (
    generate_top_contributor_figure,
    get_best_criteria,
    get_video_recommendations,
    prepare_tweet,
    tweet_top_contributor_graph,
)


class TestTournesolBot(TestCase):
    """
    TestCase of the tournesolbot.
    """

    videos = []

    def setUp(self):

        video_parameters = [
            dict(
                metadata__language="fr",
                metadata__uploader="uploader1",
                metadata__publication_date=time_ago(days=4).isoformat(),
                tournesol_score=50,
                n_comparisons=42,
                n_contributors=12,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=400).isoformat(),
                metadata__uploader="uploader2",
                tournesol_score=50,
                n_comparisons=76,
                n_contributors=24,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=15).isoformat(),
                metadata__uploader="uploader3",
                tournesol_score=50,
                n_comparisons=25,
                n_contributors=2,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=16).isoformat(),
                metadata__uploader="uploader4",
                tournesol_score=50,
                n_comparisons=6,
                n_contributors=6,
            ),
            dict(
                metadata__language="en",
                metadata__publication_date=time_ago(days=23).isoformat(),
                metadata__uploader="uploader5",
                tournesol_score=50,
                n_comparisons=47,
                n_contributors=35,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=42).isoformat(),
                metadata__uploader="uploader6",
                tournesol_score=50,
                n_comparisons=124,
                n_contributors=45,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=42).isoformat(),
                metadata__uploader="uploader7",
                tournesol_score=50,
                n_comparisons=44,
                n_contributors=25,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=42).isoformat(),
                metadata__uploader="uploader7",
                tournesol_score=-2,
                n_comparisons=44,
                n_contributors=25,
            ),
            dict(
                metadata__video_id="AAAAAAAAAAA",
                metadata__language="fr",
                metadata__publication_date=time_ago(days=85).isoformat(),
                metadata__name="Tournesol is great! 🌻 #tournesol",
                metadata__uploader="Tournesol",
                tournesol_score=50,
                n_comparisons=77,
                n_contributors=28,
            ),
        ]

        self.videos = [VideoFactory(**v) for v in video_parameters]

        Entity.objects.filter(pk=self.videos[0].pk).update(add_time=time_ago(days=4))
        Entity.objects.filter(pk=self.videos[1].pk).update(add_time=time_ago(days=400))
        Entity.objects.filter(pk=self.videos[2].pk).update(add_time=time_ago(days=29))
        Entity.objects.filter(pk=self.videos[3].pk).update(add_time=time_ago(days=42))
        Entity.objects.filter(pk=self.videos[4].pk).update(add_time=time_ago(days=76))
        Entity.objects.filter(pk=self.videos[5].pk).update(add_time=time_ago(days=29))
        Entity.objects.filter(pk=self.videos[6].pk).update(add_time=time_ago(days=42))
        Entity.objects.filter(pk=self.videos[7].pk).update(add_time=time_ago(days=42))
        Entity.objects.filter(pk=self.videos[8].pk).update(add_time=time_ago(days=76))

        # Define reliability score for videos 0 to 7
        for i, reliability_score in enumerate([29, 32, 76, 55, 26, -10, 26, 26]):
            VideoCriteriaScoreFactory(
                entity=self.videos[i],
                criteria="reliability",
                score=reliability_score,
            )

        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="largely_recommended", score=0.35
        )
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="reliability", score=32)
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="importance", score=52)
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="engaging", score=38)
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="pedagogy", score=31)
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="layman_friendly", score=26)
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="entertaining_relaxing", score=14
        )
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="better_habits", score=12)
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="diversity_inclusion", score=0.0)
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="backfire_risk", score=-2)

    def test_get_best_criteria(self):

        criteria_in_order = [
            ("importance", 52),
            ("engaging", 38),
            ("reliability", 32),
            ("pedagogy", 31),
            ("layman_friendly", 26),
            ("entertaining_relaxing", 14),
            ("better_habits", 12),
            ("diversity_inclusion", 0),
            ("backfire_risk", -2),
        ]

        assert get_best_criteria(self.videos[8], 9) == criteria_in_order
        assert get_best_criteria(self.videos[8], 2) == criteria_in_order[:2]

        with self.assertRaises(ValueError):
            get_best_criteria(self.videos[8], 15) == criteria_in_order

    @mock.patch("twitterbot.tournesolbot.get_twitter_account_from_video_id")
    def test_prepare_tweet(self, mock_get_twitter_account_from_video_id):

        tweet_text = (
            "Aujourd'hui, je recommande 'Tournesol is great! 🌻 #tournesol' de @TournesolApp, "
            "comparée 77 fois sur #Tournesol🌻 par 28 contributeurs, critères favoris:"
            "\n- Important & actionnable\n- Stimulant & suscite la réflexion"
            "\ntournesol.app/entities/yt:AAAAAAAAAAA"
        )

        mock_get_twitter_account_from_video_id.return_value = "@TournesolApp"

        assert prepare_tweet(self.videos[8]) == tweet_text

        # Test automatic shortening of the video title to fit in the tweet
        self.videos[8].metadata[
            "name"
        ] = "Tournesol is great! But this title is way to long to fit in one tweet🌻 #tournesol"

        tweet_text_too_long = (
            "Aujourd'hui, je recommande 'Tournesol is great! But this title is way to long to fit"
            " in one tw...' de @TournesolApp, comparée 77 fois sur #Tournesol🌻 par 28 "
            "contributeurs, critères favoris:"
            "\n- Important & actionnable"
            "\n- Stimulant & suscite la réflexion"
            "\ntournesol.app/entities/yt:AAAAAAAAAAA"
        )

        assert prepare_tweet(self.videos[8]) == tweet_text_too_long

        # Test replacement of special characters in the video title
        self.videos[8].metadata["name"] = "Tournesol.app is great but mention @twitter are not..."

        tweet_special_characters = (
            "Aujourd'hui, je recommande 'Tournesol․app is great but mention ﹫twitter "
            "are not...' de @TournesolApp, comparée 77 fois sur #Tournesol🌻 par 28 "
            "contributeurs, critères favoris:"
            "\n- Important & actionnable"
            "\n- Stimulant & suscite la réflexion"
            "\ntournesol.app/entities/yt:AAAAAAAAAAA"
        )

        assert prepare_tweet(self.videos[8]) == tweet_special_characters

    def test_get_video_recommendations(self):
        """
        Test function get_video_recommendations.
        """

        tweetable_videos = get_video_recommendations("fr")

        assert len(tweetable_videos) == 2
        assert self.videos[6] in tweetable_videos
        assert self.videos[8] in tweetable_videos

        assert get_video_recommendations("en")[0] == self.videos[4]

        assert not get_video_recommendations("de")

    def test_get_video_recommendations_excludes_unsafe(self):
        # Mark video 6 as unsafe, with too low trust scores
        EntityPollRating.objects.filter(entity=self.videos[6]).update(sum_trust_scores=0)

        # Only video 8 is now tweetable
        tweetable_videos = get_video_recommendations("fr")
        assert len(tweetable_videos) == 1
        assert tweetable_videos == [self.videos[8]]


class TestTournesolBotTopContributor(TestCase):
    """TestCase of the utils.contributors module."""

    def setUp(self):

        self.poll = Poll.default_poll()

        self.users = UserFactory.create_batch(15)
        self.entities = EntityFactory.create_batch(2)

        for user in self.users:
            for entity in self.entities:

                is_public = True
                ContributorRatingFactory.create(
                    user=user,
                    entity=entity,
                    is_public=is_public,
                )

            ComparisonFactory(user=user, entity_1=self.entities[0], entity_2=self.entities[1])

        now = timezone.now()
        last_month = timezone.datetime(
            now.year, now.month, 1, tzinfo=timezone.get_current_timezone()
        ) - timedelta(days=15)

        Comparison.objects.update(datetime_add=last_month)

    def test_generate_top_contributor_figure(self):
        """
        Test function generate_top_contributor_figure.
        """

        top_contributors_qs = get_top_public_contributors_last_month(
            poll_name=self.poll.name, top=10
        )

        figure_path = generate_top_contributor_figure(top_contributors_qs, "fr")

        assert figure_path.exists()

    @mock.patch("tweepy.Client")
    @mock.patch("tweepy.API")
    @override_settings(
        TWITTERBOT_CREDENTIALS={
            "@TournesolBot": {
                "LANGUAGE": "en",
                "CONSUMER_KEY": "",
                "CONSUMER_SECRET": "",
                "ACCESS_TOKEN": "",
                "ACCESS_TOKEN_SECRET": "",
            },
            "@TournesolBotFR": {
                "LANGUAGE": "fr",
                "CONSUMER_KEY": "",
                "CONSUMER_SECRET": "",
                "ACCESS_TOKEN": "",
                "ACCESS_TOKEN_SECRET": "",
            },
        }
    )
    def test_tweet_top_contributor_graph(self, api_mock, client_mock):
        mocked_api_client = api_mock.return_value
        mocked_v2_client = client_mock.return_value

        tweet_top_contributor_graph("@TournesolBot", assumeyes=True)
        tweet_top_contributor_graph("@TournesolBotFR", assumeyes=True)

        self.assertEqual(
            mocked_api_client.media_upload.call_count, 2, mocked_api_client.media_upload.calls
        )
        self.assertEqual(mocked_api_client.media_upload.call_args_list[0].args[0].suffix, ".png")
        self.assertEqual(
            mocked_v2_client.create_tweet.call_count, 2, mocked_api_client.update_status.calls
        )
