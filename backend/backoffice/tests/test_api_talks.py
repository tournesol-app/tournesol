"""
All test cases of the `faq` views.
"""
import datetime

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from backoffice.models import TalkEntry


def create_talk_entry(name):
    return TalkEntry.objects.create(name=name)


class TalksListViewTestCase(TestCase):
    """
    TestCase of the `TalkEntryListView` view.
    """

    default_lang = "en"
    available_lang = "fr"
    unavailable_lang = "zz"

    def setUp(self):
        self.client = APIClient()
        self.talk_base_url = "/talks/"

        self.talk = create_talk_entry("the_first_talk")

    def test_anon_200_list(self):
        """
        An anonymous user can access the Talk.
        """
        response = self.client.get(self.talk_base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_talks_are_not_display(self):
        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        # all talks are display by defaults
        self.assertEqual(0, len(results))

    def test_list_talks_displayed(self):

        self.talk.display = True
        self.talk.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        # all talks are display by defaults
        self.assertEqual(1, len(results))
        self.assertDictEqual(
            results[0],
            {
                "name": self.talk.name,
                "title": None,
                "abstract": None,
                "invitation_link": None,
                "youtube_link": None,
                "speaker": None,
                "speaker_short_desc": None,
                "date": None,
                "date_gmt": None
            },
        )

    def test_list_talks_displayed_with_data(self):
        self.talk.display = True
        self.talk.save()

        self.other_talk = create_talk_entry("the_second_talk")
        self.other_talk.title = 'a title'
        self.other_talk.abstract = 'an abstract'
        self.other_talk.invitation_link = 'https://wikipedia.fr'
        self.other_talk.youtube_link = 'https://you.tube'
        self.other_talk.speaker = 'a speaker'
        self.other_talk.speaker_short_desc = 'a speaker bio'
        datetime_str = '09/19/22 13:55:26'
        self.other_talk.date = datetime.datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        self.other_talk.display = True
        self.other_talk.save()

        response = self.client.get(self.talk_base_url)
        results = response.data["results"]

        # all talks are display by defaults
        self.assertEqual(2, len(results))
        self.assertDictEqual(
            results[0],
            {
                "name": self.other_talk.name,
                "title": 'a title',
                "abstract": 'an abstract',
                "invitation_link": 'https://wikipedia.fr',
                "youtube_link": 'https://you.tube',
                "speaker": 'a speaker',
                "speaker_short_desc": 'a speaker bio',
                "date": '2022-09-19T13:55:26Z',
                "date_gmt": '2022-09-19T15:55:26+02:00'
            },
        )
        self.assertDictEqual(
            results[1],
            {
                "name": self.talk.name,
                "title": None,
                "abstract": None,
                "invitation_link": None,
                "youtube_link": None,
                "speaker": None,
                "speaker_short_desc": None,
                "date": None,
                "date_gmt": None
            },
        )
        self.maxDiff = None
