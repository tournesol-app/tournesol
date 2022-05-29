

from datetime import datetime, timedelta

from django.test import TestCase

from core.tests.factories.user import UserFactory
from tournesol.models import Poll
from tournesol.models.comparisons import Comparison
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import EntityFactory
from tournesol.tests.factories.ratings import ContributorRatingFactory
from twitterbot.best_contributors import get_previous_month_best_public_contributor


class TestBestContributor(TestCase):
    """TestCase for the best contributors of last month."""
    
    def setUp(self):

        self.poll = Poll.default_poll()
        
        self.users = UserFactory.create_batch(5)
        self.entities = EntityFactory.create_batch(6)

        for user in self.users:
            for entity in self.entities:
                
                is_public = True
                if user==self.users[2] and entity==self.entities[4]:
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
        
        now = datetime.now()
        last_month = datetime(now.year, now.month, 1) - timedelta(days=15)
        
        for comparison in self.comparisons:
            Comparison.objects.filter(pk=comparison.pk).update(datetime_add=last_month)

    def test_get_previous_month_best_public_contributor(self):
        """Test best public contributor of the previous month."""
        
        best_contributors = get_previous_month_best_public_contributor()
        
        assert best_contributors[0] == (self.users[2].username, 5)
        assert best_contributors[1] == (self.users[0].username, 4)
        assert best_contributors[2] == (self.users[3].username, 3)
        assert best_contributors[3] == (self.users[1].username, 2)
        assert best_contributors[4] == (self.users[4].username, 1)
        