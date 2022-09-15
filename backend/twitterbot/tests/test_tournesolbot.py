from unittest.mock import patch

from django.test import TestCase

from core.utils.time import time_ago
from tournesol.models import Entity
from tournesol.tests.factories.entity import VideoCriteriaScoreFactory, VideoFactory
from twitterbot.tournesolbot import get_best_criteria, get_video_recommendations, prepare_tweet


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
                rating_n_ratings=42,
                rating_n_contributors=12,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=400).isoformat(),
                metadata__uploader="uploader2",
                tournesol_score=50,
                rating_n_ratings=76,
                rating_n_contributors=24,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=15).isoformat(),
                metadata__uploader="uploader3",
                tournesol_score=50,
                rating_n_ratings=25,
                rating_n_contributors=2,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=16).isoformat(),
                metadata__uploader="uploader4",
                tournesol_score=50,
                rating_n_ratings=6,
                rating_n_contributors=6,
            ),
            dict(
                metadata__language="en",
                metadata__publication_date=time_ago(days=23).isoformat(),
                metadata__uploader="uploader5",
                tournesol_score=50,
                rating_n_ratings=47,
                rating_n_contributors=35,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=42).isoformat(),
                metadata__uploader="uploader6",
                tournesol_score=50,
                rating_n_ratings=124,
                rating_n_contributors=45,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=42).isoformat(),
                metadata__uploader="uploader7",
                tournesol_score=50,
                rating_n_ratings=44,
                rating_n_contributors=25,
            ),
            dict(
                metadata__language="fr",
                metadata__publication_date=time_ago(days=42).isoformat(),
                metadata__uploader="uploader7",
                tournesol_score=-2,
                rating_n_ratings=44,
                rating_n_contributors=25,
            ),
            dict(
                metadata__video_id="AAAAAAAAAAA",
                metadata__language="fr",
                metadata__publication_date=time_ago(days=85).isoformat(),
                metadata__name="Tournesol is great! 🌻 #tournesol",
                metadata__uploader="Tournesol",
                tournesol_score=50,
                rating_n_ratings=77,
                rating_n_contributors=28,
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
        for i, reliability_score in enumerate([29, 32, 76, 55, 22, -10, 25, 25]):
            VideoCriteriaScoreFactory(
                entity=self.videos[i],
                criteria="reliability",
                score=reliability_score,
            )

        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="largely_recommended", score=0.35
        )
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="reliability", score=32
        )
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="importance", score=52
        )
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="engaging", score=38)
        VideoCriteriaScoreFactory(entity=self.videos[8], criteria="pedagogy", score=31)
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="layman_friendly", score=26
        )
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="entertaining_relaxing", score=14
        )
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="better_habits", score=12
        )
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="diversity_inclusion", score=0.0
        )
        VideoCriteriaScoreFactory(
            entity=self.videos[8], criteria="backfire_risk", score=-2
        )

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

    @patch("twitterbot.tournesolbot.get_twitter_account_from_video_id")
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
        self.videos[8].metadata[
            "name"
        ] = "Tournesol.app is great but mention @twitter are not..."

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
