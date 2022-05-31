from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.tests.factories.user import UserFactory
from core.utils.time import time_ago
from tournesol.models import Poll
from tournesol.models.comparisons import Comparison
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import EntityFactory
from tournesol.tests.factories.ratings import ContributorRatingFactory
from tournesol.utils.contributors import get_last_month_top_public_contributors


class UtilsContributorsTestCase(TestCase):
    """TestCase of the utils.contributors module."""

    def setUp(self):

        self.poll = Poll.default_poll()

        self.users = UserFactory.create_batch(5)
        self.entities = EntityFactory.create_batch(6)

        for user in self.users:
            for entity in self.entities:

                is_public = True
                if user == self.users[2] and entity == self.entities[4]:
                    is_public = False

                ContributorRatingFactory.create(
                    user=user,
                    entity=entity,
                    is_public=is_public,
                )

        comparisons_parameters = [
            dict(user=self.users[2], entity_1=self.entities[0], entity_2=self.entities[1]),
            dict(user=self.users[2], entity_1=self.entities[0], entity_2=self.entities[2]),
            dict(user=self.users[2], entity_1=self.entities[0], entity_2=self.entities[3]),
            dict(user=self.users[2], entity_1=self.entities[0], entity_2=self.entities[4]),
            dict(user=self.users[2], entity_1=self.entities[0], entity_2=self.entities[5]),
            dict(user=self.users[2], entity_1=self.entities[1], entity_2=self.entities[5]),
            dict(user=self.users[0], entity_1=self.entities[0], entity_2=self.entities[1]),
            dict(user=self.users[0], entity_1=self.entities[0], entity_2=self.entities[2]),
            dict(user=self.users[0], entity_1=self.entities[0], entity_2=self.entities[3]),
            dict(user=self.users[0], entity_1=self.entities[1], entity_2=self.entities[5]),
            dict(user=self.users[3], entity_1=self.entities[0], entity_2=self.entities[1]),
            dict(user=self.users[3], entity_1=self.entities[0], entity_2=self.entities[2]),
            dict(user=self.users[3], entity_1=self.entities[0], entity_2=self.entities[3]),
            dict(user=self.users[1], entity_1=self.entities[0], entity_2=self.entities[1]),
            dict(user=self.users[1], entity_1=self.entities[0], entity_2=self.entities[2]),
            dict(user=self.users[4], entity_1=self.entities[0], entity_2=self.entities[1]),
        ]

        self.comparisons = [ComparisonFactory(**c) for c in comparisons_parameters]

        now = timezone.now()
        last_month = timezone.datetime(
            now.year, now.month, 1, tzinfo=timezone.get_current_timezone()
        ) - timedelta(days=15)

        for comparison in self.comparisons:
            Comparison.objects.filter(pk=comparison.pk).update(datetime_add=last_month)

        # Comparisons with other dates to be sure it only gets those from the previous month
        ComparisonFactory(
            user=self.users[4], entity_1=self.entities[1], entity_2=self.entities[2]
        )
        older_comparison = ComparisonFactory(
            user=self.users[4], entity_1=self.entities[1], entity_2=self.entities[3]
        )
        Comparison.objects.filter(pk=older_comparison.pk).update(
            datetime_add=time_ago(days=65)
        )

    def test_get_last_month_top_public_contributors(self):
        """Test top public contributor of the previous month."""

        top_contributors = get_last_month_top_public_contributors(
            poll_name=self.poll.name
        )

        self.assertEqual(top_contributors[0], (self.users[2].username, 5))
        self.assertEqual(top_contributors[1], (self.users[0].username, 4))
        self.assertEqual(top_contributors[2], (self.users[3].username, 3))
        self.assertEqual(top_contributors[3], (self.users[1].username, 2))
        self.assertEqual(top_contributors[4], (self.users[4].username, 1))
