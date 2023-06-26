from datetime import timedelta

from django.utils import timezone
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from backoffice.models import TalkEntry


def create_talk_entry(name, displayed):
    return TalkEntry.objects.create(
        name=name,
        title=f"{name}_title",
        speakers=f"{name}_speakers",
        abstract=f"{name}_abstract",
        display=displayed,
    )


class TalksListViewTestCase(TestCase):
    """
    TestCase of the `TalkEntryListView` view.
    """

    def setUp(self):
        self.client = APIClient()
        self.talk_base_url = "/backoffice/talks/"

        self.talk_displayed = create_talk_entry("talk_displayed", displayed=True)
        self.talk_hidden = create_talk_entry("talk_hidden", displayed=False)

    def test_anonymous_can_list(self):
        """
        An anonymous user can list the Talks.
        """
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)

    def test_list_return_all_expected_fields(self):
        """
        Only the expected fields are returned by the API.
        """
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)

        talk_name = self.talk_displayed.name
        self.assertDictEqual(
            results[0],
            {
                "name": talk_name,
                "title": f"{talk_name}_title",
                "date": None,
                "date_as_tz_europe_paris": None,
                "speakers": f"{talk_name}_speakers",
                "abstract": f"{talk_name}_abstract",
                "invitation_link": None,
                "youtube_link": None,
            },
        )

    def test_list_only_displayed_talks(self):
        """
        Only displayed Talks can be listed.
        """
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], self.talk_displayed.name)

        self.talk_hidden.display = True
        self.talk_hidden.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

        TalkEntry.objects.update(display=False)
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    def test_list_ordering(self):
        """
        The Talks should be ordered by date in the descending order.
        """
        now = timezone.now()
        future = now + timedelta(days=1)

        self.talk_displayed.date = now
        self.talk_displayed.save()

        self.talk_hidden.display = True
        self.talk_hidden.date = None
        self.talk_hidden.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        # The Talks with no date should be listed last.
        self.assertEqual(results[0]["name"], self.talk_displayed.name)
        self.assertEqual(results[1]["name"], self.talk_hidden.name)

        self.talk_hidden.date = future
        self.talk_hidden.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        # The Talks should be ordered by date desc.
        self.assertEqual(results[0]["name"], self.talk_hidden.name)
        self.assertEqual(results[1]["name"], self.talk_displayed.name)
