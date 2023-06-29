from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from backoffice.models.banner import Banner, BannerText, BannerTitle
from core.utils.time import time_ago, time_ahead
from tournesol.tests.utils.mock_now import MockNow


def create_banner(name, date_start, date_end, enabled):
    return Banner.objects.create(
        name=name,
        date_start=date_start,
        date_end=date_end,
        enabled=enabled,        
    )

def create_title_banner(banner, language, title):
    return BannerTitle.objects.create(
        banner=banner,
        language=language,
        title=title,
    )

def create_text_banner(banner, language, text):
    return BannerText.objects.create(
        banner=banner,
        language=language,
        text=text,
    )

class BannersListViewTestCase(TestCase):
    """
    TestCase of the `BannerListView` view.
    """

    @MockNow.Context()
    def setUp(self):
        self.client = APIClient()
        self.banner_base_url = "/backoffice/banners/"

        self.banner_enabled_ongoing = create_banner(
            "banner_enabled_ongoing", time_ago(days=2), time_ahead(days=2), True
        )
        self.banner_enabled_old = create_banner(
            "banner_enabled_old", time_ago(days=10), time_ago(days=5), True
        )
        self.banner_disabled = create_banner(
            "banner_disabled", time_ago(days=2), time_ahead(days=2), False
        )

    @MockNow.Context()
    def test_anonymous_can_list(self):
        """
        An anonymous user can list the Banners.
        """
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)

    @MockNow.Context()
    def test_list_return_all_expected_fields(self):
        """
        Only the expected fields are returned by the API.
        """
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertDictEqual(
            results[0],
            {
                "name": self.banner_enabled_ongoing.name,
                "title": "",
                "text": "",
                "date_start": "2019-12-30T00:00:00Z",
                "date_end": "2020-01-03T00:00:00Z",
                "priority": 5,
                "security_advisory": False,
            },
        )

    @MockNow.Context()
    def test_list_only_enabled_banners(self):
        """
        Only enabled Banners can be listed.
        """
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], self.banner_enabled_ongoing.name)

        self.banner_disabled.enabled = True
        self.banner_disabled.save()

        response = self.client.get(self.banner_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

        Banner.objects.update(enabled=False)
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    @MockNow.Context()
    def test_list_only_ongoing_banners(self):
        """
        Only ongoing Banners can be listed.
        """
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], self.banner_enabled_ongoing.name)

        self.banner_enabled_old.date_end = time_ahead(days=2)
        self.banner_enabled_old.save()

        response = self.client.get(self.banner_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

        Banner.objects.update(date_end=time_ago(days=2))
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    @MockNow.Context()
    def test_language_requested(self):
        """
        Return the banner in the requested language.
        If it does not exist, return the default language.
        If there is no default language, return emptry string.
        """
        english_title = create_title_banner(
            self.banner_enabled_ongoing, "en", "English title"
        )
        french_title = create_title_banner(
            self.banner_enabled_ongoing, "fr", "French title"
        )
        english_text = create_text_banner(
            self.banner_enabled_ongoing, "en", "English text"
        )
        french_text = create_text_banner(
            self.banner_enabled_ongoing, "fr", "French text"
        )
        
        self.client.credentials(HTTP_ACCEPT_LANGUAGE="fr")
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertDictEqual(
            results[0],
            {
                "name": self.banner_enabled_ongoing.name,
                "title": french_title.title,
                "text": french_text.text,
                "date_start": "2019-12-30T00:00:00Z",
                "date_end": "2020-01-03T00:00:00Z",
                "priority": 5,
                "security_advisory": False,
            },
        )

        french_text.delete()
        french_title.delete()
        self.client.credentials(HTTP_ACCEPT_LANGUAGE="fr")
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertDictEqual(
            results[0],
            {
                "name": self.banner_enabled_ongoing.name,
                "title": english_title.title,
                "text": english_text.text,
                "date_start": "2019-12-30T00:00:00Z",
                "date_end": "2020-01-03T00:00:00Z",
                "priority": 5,
                "security_advisory": False,
            },
        )

        english_text.delete()
        english_title.delete()
        self.client.credentials(HTTP_ACCEPT_LANGUAGE="fr")
        response = self.client.get(self.banner_base_url)
        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertDictEqual(
            results[0],
            {
                "name": self.banner_enabled_ongoing.name,
                "title": "",
                "text": "",
                "date_start": "2019-12-30T00:00:00Z",
                "date_end": "2020-01-03T00:00:00Z",
                "priority": 5,
                "security_advisory": False,
            },
        )