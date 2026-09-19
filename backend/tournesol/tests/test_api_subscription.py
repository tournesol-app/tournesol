from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models.entity_source import EntitySource
from tournesol.models.subscription import Subscription
from tournesol.tests.factories.subscription import EntitySourceFactory, SubscriptionFactory

CHANNEL_ID = "UCH8TsmKEX_PR4jxsg2W3vOg"
CHANNEL_UID = f"yt:{CHANNEL_ID}"

# A sample of what the YouTube API returns for `channels().list(part="snippet")`.
CHANNEL_API_RESPONSE = {
    "kind": "youtube#channelListResponse",
    "pageInfo": {"totalResults": 1, "resultsPerPage": 5},
    "items": [
        {
            "kind": "youtube#channel",
            "etag": "ntdShdXlk7wT8kjjPpNj9jwgyH4",
            "id": CHANNEL_ID,
            "snippet": {
                "title": "Tournesol",
                "description": "Channel description",
                "publishedAt": "2021-01-01T00:00:00Z",
                "thumbnails": {
                    "default": {"url": "https://yt3.ggpht.com/default"},
                    "medium": {"url": "https://yt3.ggpht.com/medium"},
                    "high": {"url": "https://yt3.ggpht.com/high"},
                },
            },
        }
    ],
}
# What `get_channel_metadata` extracts from the response above.
CHANNEL_METADATA = {
    "name": "Tournesol",
    "thumbnail": "https://yt3.ggpht.com/medium",
}


class SubscriptionApiTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.user = UserFactory(username="subscriber")
        self.other_user = UserFactory(username="someone_else")
        self.subscriptions_base_url = "/users/me/subscriptions/"

    def test_anonymous_cannot_use_the_api(self):
        self.assertEqual(
            self.client.get(self.subscriptions_base_url).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            self.client.post(
                self.subscriptions_base_url,
                {"entity_source": {"uid": CHANNEL_UID}},
                format="json",
            ).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    @patch("tournesol.utils.api_youtube.get_youtube_channel_details")
    def test_can_subscribe_to_a_new_source(self, mock_get_youtube_channel_details):
        mock_get_youtube_channel_details.return_value = CHANNEL_API_RESPONSE
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": CHANNEL_UID}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["entity_source"],
            {
                "uid": CHANNEL_UID,
                "metadata": CHANNEL_METADATA,
            },
        )
        self.assertIn("created_at", response.data)
        mock_get_youtube_channel_details.assert_called_once_with(CHANNEL_ID)

        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(subscription.entity_source.uid, CHANNEL_UID)

    @patch("tournesol.utils.api_youtube.get_youtube_channel_details")
    def test_cannot_subscribe_to_a_nonexistent_source(self, mock_get_youtube_channel_details):
        mock_get_youtube_channel_details.return_value = {"items": []}
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": CHANNEL_UID}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(EntitySource.objects.filter(uid=CHANNEL_UID).exists())
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())

    @patch("tournesol.utils.api_youtube.get_youtube_channel_details")
    def test_subscribing_stores_the_source_without_a_thumbnail(
        self, mock_get_youtube_channel_details
    ):
        mock_get_youtube_channel_details.return_value = {
            "items": [{"id": CHANNEL_ID, "snippet": {"title": "Tournesol"}}]
        }
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": CHANNEL_UID}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["entity_source"]["metadata"],
            {"name": "Tournesol", "thumbnail": None},
        )

    @override_settings(YOUTUBE_API_KEY=None)
    def test_subscribing_without_an_api_key_still_creates_the_source(self):
        """
        When the metadata cannot be fetched (no API key configured), the
        subscription is created anyway with an empty metadata, to be filled in
        later.
        """
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": CHANNEL_UID}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["entity_source"]["metadata"], {})
        self.assertTrue(Subscription.objects.filter(user=self.user).exists())

    @patch("tournesol.utils.api_youtube.get_youtube_channel_details")
    def test_subscribing_when_youtube_fails_still_creates_the_source(
        self, mock_get_youtube_channel_details
    ):
        """
        When the YouTube API call fails, the subscription is created anyway with
        an empty metadata, to be filled in later.
        """
        mock_get_youtube_channel_details.side_effect = Exception("YouTube is unreachable")
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": CHANNEL_UID}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["entity_source"]["metadata"], {})
        self.assertTrue(Subscription.objects.filter(user=self.user).exists())

    @patch("tournesol.utils.api_youtube.get_youtube_channel_details")
    def test_subscribing_reuses_an_existing_source(self, mock_get_youtube_channel_details):
        self.client.force_authenticate(self.user)
        source = EntitySourceFactory(uid=CHANNEL_UID)

        self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": CHANNEL_UID}},
            format="json",
        )

        mock_get_youtube_channel_details.assert_not_called()
        self.assertEqual(EntitySource.objects.filter(uid=CHANNEL_UID).count(), 1)
        self.assertEqual(
            Subscription.objects.get(user=self.user).entity_source, source
        )

    def test_cannot_subscribe_twice_to_the_same_source(self):
        self.client.force_authenticate(self.user)
        SubscriptionFactory(
            user=self.user, entity_source=EntitySourceFactory(uid=CHANNEL_UID)
        )

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": CHANNEL_UID}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_cannot_subscribe_with_an_unknown_namespace(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": f"xx:{CHANNEL_ID}"}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_subscribe_with_a_malformed_channel_id(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.subscriptions_base_url,
            {"entity_source": {"uid": "yt:not-a-channel"}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_returns_only_the_logged_user_subscriptions(self):
        self.client.force_authenticate(self.user)
        mine = SubscriptionFactory(user=self.user)
        SubscriptionFactory(user=self.other_user)

        response = self.client.get(self.subscriptions_base_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["entity_source"]["uid"],
            mine.entity_source.uid,
        )

    def test_can_retrieve_a_subscription_by_source_uid(self):
        self.client.force_authenticate(self.user)
        SubscriptionFactory(
            user=self.user, entity_source=EntitySourceFactory(uid=CHANNEL_UID)
        )

        response = self.client.get(f"{self.subscriptions_base_url}{CHANNEL_UID}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["entity_source"]["uid"], CHANNEL_UID)

    def test_cannot_retrieve_another_user_subscription(self):
        self.client.force_authenticate(self.user)
        SubscriptionFactory(
            user=self.other_user, entity_source=EntitySourceFactory(uid=CHANNEL_UID)
        )

        response = self.client.get(f"{self.subscriptions_base_url}{CHANNEL_UID}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_unsubscribe(self):
        self.client.force_authenticate(self.user)
        source = EntitySourceFactory(uid=CHANNEL_UID)
        SubscriptionFactory(user=self.user, entity_source=source)

        response = self.client.delete(f"{self.subscriptions_base_url}{CHANNEL_UID}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())
        self.assertTrue(EntitySource.objects.filter(uid=CHANNEL_UID).exists())

    def test_cannot_unsubscribe_from_a_source_not_subscribed_to(self):
        self.client.force_authenticate(self.user)
        EntitySourceFactory(uid=CHANNEL_UID)

        response = self.client.delete(f"{self.subscriptions_base_url}{CHANNEL_UID}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_unsubscribe_from_another_user_subscription(self):
        self.client.force_authenticate(self.user)
        source = EntitySourceFactory(uid=CHANNEL_UID)
        SubscriptionFactory(user=self.other_user, entity_source=source)

        response = self.client.delete(f"{self.subscriptions_base_url}{CHANNEL_UID}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Subscription.objects.filter(user=self.other_user).exists())
