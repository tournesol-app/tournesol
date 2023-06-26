"""
All test cases of the `TalkEntry` model.
"""

from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from backoffice.models import TalkEntry


class TalkEntryTestCase(TestCase):
    def test_name_are_automatically_generated(self):
        talk = TalkEntry.objects.create(title="The first talk")
        self.assertEqual(talk.name, slugify(talk.title))

    def test_name_are_not_automatically_overriden(self):
        talk = TalkEntry.objects.create(title="The first talk", name="custom-name")
        self.assertEqual(talk.name, "custom-name")

    def test_name_collisions_are_raised(self):
        TalkEntry.objects.create(title="The first talk")

        with self.assertRaises(IntegrityError):
            TalkEntry.objects.create(title="The second talk", name="the-first-talk")
