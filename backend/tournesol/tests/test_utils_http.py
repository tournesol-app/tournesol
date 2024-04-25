from django.test import TestCase

from tournesol.utils.http import langs_from_header_accept_language


class HTTPUtilsTestCase(TestCase):
    def test_langs_from_header_accept_language(self):
        langs = langs_from_header_accept_language("")
        self.assertEqual(langs, [])

        langs = langs_from_header_accept_language("fr")
        self.assertEqual(langs, ["fr"])

        langs = langs_from_header_accept_language("da, en-gb;q=0.8, en;q=0.7")
        self.assertEqual(langs, ["da", "en-gb", "en"])
