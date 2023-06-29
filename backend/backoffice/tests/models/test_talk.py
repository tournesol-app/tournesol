"""
All test cases of the `TalkEntry` model.
"""

import random
import string

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from backoffice.models.talk import TalkEntry
from tournesol.tests.utils.mock_now import MockNow


class TalkEntryFieldsTestCase(TestCase):
    """
    This test case contains all tests related to the model fields and their
    expected configuration.
    """

    def test_field_name_max_length(self):
        """
        The field `name` should be able to handle titles containing 255
        characters.
        """
        talk = TalkEntry.objects.create(
            title="".join(random.choice(string.ascii_lowercase) for i in range(255))
        )
        self.assertEqual(talk.name, slugify(talk.title))


class TalkEntrySaveTestCase(TestCase):
    """
    This test case contains all tests related to behaviour of the model's
    save() method.
    """

    def test_save_name_is_automatically_generated(self):
        talk = TalkEntry.objects.create(title="The first talk")
        self.assertEqual(talk.name, slugify(talk.title))

    def test_save_name_is_not_automatically_overriden(self):
        talk = TalkEntry.objects.create(title="The first talk", name="custom-name")
        self.assertEqual(talk.name, "custom-name")

    def test_save_name_collisions_are_raised(self):
        TalkEntry.objects.create(title="The first talk")

        with self.assertRaises(IntegrityError):
            TalkEntry.objects.create(title="The second talk", name="the-first-talk")


class TalkEntryMethodsTestCase(TestCase):
    """
    This test case contains all tests related to behaviour of the model's
    methods.

    See the `TalkEntrySaveTestCase` for the specific behaviour of the save()
    method.
    """

    @MockNow.Context()
    def test_date_as_tz_europe_paris(self):
        """
        Test the behaviour of the `date_as_tz_europe_paris` method.
        """
        # [GIVEN] A Talk created without a date.
        talk = TalkEntry.objects.create(title="The first talk")

        # [THEN] No default date should be set.
        self.assertEqual(talk.date, None)
        # [THEN] The Europe/Paris date should also be empty.
        self.assertEqual(talk.date_as_tz_europe_paris(), None)

        # [WHEN] A date is set.
        talk.date = timezone.now()
        talk.save(update_fields=["date"])
        # [THEN] The Europe/Paris date should also be set.
        self.assertEqual(talk.date_as_tz_europe_paris(), "2020-01-01T01:00:00+0100")
