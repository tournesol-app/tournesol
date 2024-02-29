from datetime import timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from backoffice.models.talk import TalkEntry
from core.utils.time import time_ago, time_ahead
from tournesol.tests.utils.mock_now import MockNow


def create_event(name, date, public, event_type):
    return TalkEntry.objects.create(
        name=name,
        date=date,
        event_type=event_type,
        title=f"{name}_title",
        speakers=f"{name}_speakers",
        abstract=f"{name}_abstract",
        public=public,
    )


class TournesolEventListViewTestCase(TestCase):
    """
    TestCase of the `TournesolEventListView` view.
    """

    @MockNow.Context()
    def setUp(self):
        self.client = APIClient()
        self.events_base_url = "/backoffice/events/"

        self.live_public = create_event(
            "live_public", date=time_ago(days=8), public=True, event_type=TalkEntry.EVENT_TYPE_LIVE
        )
        self.live_private = create_event(
            "live_private",
            date=time_ahead(days=8),
            public=False,
            event_type=TalkEntry.EVENT_TYPE_LIVE,
        )
        self.talk_public = create_event(
            "talk_public",
            date=time_ago(days=10),
            public=True,
            event_type=TalkEntry.EVENT_TYPE_TALK,
        )
        self.talk_private = create_event(
            "talk_private",
            date=time_ahead(days=10),
            public=False,
            event_type=TalkEntry.EVENT_TYPE_TALK,
        )

    def test_anonymous_can_list(self):
        """
        An anonymous user can list the events.
        """
        response = self.client.get(self.events_base_url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 2)

    def test_list_return_all_expected_fields(self):
        """
        Only the expected fields are returned by the API.
        """
        response = self.client.get(self.events_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 2)

        live = self.live_public
        talk = self.talk_public

        self.assertDictEqual(
            results[0],
            {
                "name": live.name,
                "title": live.title,
                "event_type": "live",
                "date": "2019-12-24T00:00:00Z",
                "date_as_tz_europe_paris": "2019-12-24T01:00:00+0100",
                "speakers": live.speakers,
                "abstract": live.abstract,
                "invitation_link": None,
                "youtube_link": None,
            },
        )

    def test_list_only_public_events(self):
        """
        Only public events can be listed.
        """
        response = self.client.get(self.events_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], self.live_public.name)
        self.assertEqual(results[1]["name"], self.talk_public.name)

        TalkEntry.objects.update(public=False)
        response = self.client.get(self.events_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 0)

        TalkEntry.objects.update(public=True)
        response = self.client.get(self.events_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_list_only_scheduled_events(self):
        """
        Only scheduled events can be listed.
        """
        TalkEntry.objects.update(public=True)
        TalkEntry.objects.update(date=None)

        response = self.client.get(self.events_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    def test_list_filtered_by_event_type(self):
        """
        The events can be filtered by type.
        """
        response = self.client.get(self.events_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], self.live_public.name)

        response = self.client.get(self.events_base_url, {"event_type": "talk"})
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], self.talk_public.name)

    def test_list_ordering(self):
        """
        The events should be ordered by date in the descending order.
        """
        TalkEntry.objects.update(public=True)

        response = self.client.get(self.events_base_url)
        results = response.data["results"]

        # The private events are in the future, and should be listed first.
        self.assertEqual(results[0]["name"], self.talk_private.name)
        self.assertEqual(results[1]["name"], self.live_private.name)
        self.assertEqual(results[2]["name"], self.live_public.name)
        self.assertEqual(results[3]["name"], self.talk_public.name)

        self.talk_private.date = self.talk_public.date - timedelta(days=1)
        self.talk_private.save(update_fields=["date"])

        response = self.client.get(self.events_base_url)
        results = response.data["results"]

        self.assertEqual(results[0]["name"], self.live_private.name)
        self.assertEqual(results[1]["name"], self.live_public.name)
        self.assertEqual(results[2]["name"], self.talk_public.name)
        self.assertEqual(results[3]["name"], self.talk_private.name)
