from datetime import timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from backoffice.models.talk import TalkEntry
from core.utils.time import time_ago, time_ahead
from tournesol.tests.utils.mock_now import MockNow


def create_talk_entry(name, date, public):
    return TalkEntry.objects.create(
        name=name,
        date=date,
        event_type="TALK",
        title=f"{name}_title",
        speakers=f"{name}_speakers",
        abstract=f"{name}_abstract",
        public=public,
    )


class TalksListViewTestCase(TestCase):
    """
    TestCase of the `TalkEntryListView` view.
    """

    @MockNow.Context()
    def setUp(self):
        self.client = APIClient()
        self.talk_base_url = "/backoffice/talks/"

        self.talk_public = create_talk_entry(
            "talk_public", date=time_ago(days=10), public=True
        )
        self.talk_private = create_talk_entry(
            "talk_private", date=time_ahead(days=10), public=False
        )

    def test_anonymous_can_list(self):
        """
        An anonymous user can list the Talks.
        """
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)

    @MockNow.Context()
    def test_list_return_all_expected_fields(self):
        """
        Only the expected fields are returned by the API.
        """
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)

        talk = self.talk_public
        self.assertDictEqual(
            results[0],
            {
                "name": talk.name,
                "title": talk.title,
                "event_type": "TALK",
                "date": "2019-12-22T00:00:00Z",
                "date_as_tz_europe_paris": "2019-12-22T01:00:00+0100",
                "speakers": talk.speakers,
                "abstract": talk.abstract,
                "invitation_link": None,
                "youtube_link": None,
            },
        )

    def test_list_only_public_talks(self):
        """
        Only public Talks can be listed.
        """
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], self.talk_public.name)

        self.talk_private.public = True
        self.talk_private.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

        TalkEntry.objects.update(public=False)
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    def test_list_only_scheduled_talks(self):
        """
        Only scheduled Talks can be listed.
        """
        TalkEntry.objects.update(public=True)
        TalkEntry.objects.update(date=None)

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    def test_list_ordering(self):
        """
        The Talks should be ordered by date in the descending order.
        """

        self.talk_private.public = True
        self.talk_private.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        # The private Talks is in the future, and should be listed first.
        self.assertEqual(results[0]["name"], self.talk_private.name)
        self.assertEqual(results[1]["name"], self.talk_public.name)

        self.talk_private.date = self.talk_public.date - timedelta(days=1)
        self.talk_private.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        # The order should now be reversed.
        self.assertEqual(results[0]["name"], self.talk_public.name)
        self.assertEqual(results[1]["name"], self.talk_private.name)
