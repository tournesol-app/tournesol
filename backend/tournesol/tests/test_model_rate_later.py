"""
All test cases of the `RateLater` model.
"""

from django.db import IntegrityError, transaction
from django.test import TestCase

from core.tests.factories.user import UserFactory
from tournesol.models.rate_later import RateLater
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollFactory


class RateLaterTestCase(TestCase):
    """
    TestCase of the `RateLater` model.
    """

    _user = "username"

    def setUp(self):
        self.video = VideoFactory()
        self.user = UserFactory(username=self._user)
        self.poll = PollFactory()

    def test_required_fields(self):
        """
        A `RateLater` item cannot be created without explicit entity, user and
        poll.
        """
        # The entity field is not enough.
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                RateLater.objects.create(entity=self.video)

        # The user field is not enough.
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                RateLater.objects.create(user=self.user)

        # The poll field is not enough.
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                RateLater.objects.create(poll=self.poll)

        rate_later = RateLater(entity=self.video, user=self.user)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                rate_later.save()

        rate_later.poll = self.poll
        rate_later.save()

    def test_field_created_at(self):
        """
        The `created_at` field must be automatically set by the database.
        """
        rate_later = RateLater.objects.create(
            entity=self.video, user=self.user, poll=self.poll
        )
        self.assertIsNotNone(rate_later.created_at)
