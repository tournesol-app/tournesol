"""
All test cases of the `ComparisonCriteriaScore` model.
"""

from unittest.mock import Mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.tests.factories.user import UserFactory
from tournesol.models import ComparisonCriteriaScore
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory


class ComparisonCriteriaScoreTestCase(TestCase):
    """
    TestCase of the `ComparisonCriteriaScore` model.
    """

    _user = "username"

    def setUp(self):
        self.poll = PollWithCriteriasFactory()
        self.user = UserFactory(username=self._user)
        self.comparison = ComparisonFactory(poll=self.poll, user=self.user)

    def test_score_max_validators(self):
        score = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=0,
            score_max=0,
        )

        # score_max cannot be zero.
        with self.assertRaises(ValidationError):
            score.clean_fields()

        score.score_max = -1
        # score_max cannot be negative.
        with self.assertRaises(ValidationError):
            score.clean_fields()

        score.score_max = 1
        score.clean_fields()

    def test_validate_score_max(self):
        score_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=11,
            score_max=10,
        )

        # The score cannot be greater than score_max.
        with self.assertRaises(ValueError):
            score_test.validate_score_max(
                score=score_test.score,
                score_max=score_test.score_max,
                criterion=score_test.criteria,
            )

        score_test.score = -11
        # The absolute value of the score cannot be greater than score_max.
        with self.assertRaises(ValueError):
            score_test.validate_score_max(
                score=score_test.score,
                score_max=score_test.score_max,
                criterion=score_test.criteria,
            )

        # The score can be zero.
        score_test.score = 0
        score_test.validate_score_max(
            score=score_test.score,
            score_max=score_test.score_max,
            criterion=score_test.criteria,
        )

        # The score can be equal to the score_max.
        score_test.score = score_test.score_max
        score_test.validate_score_max(
            score=score_test.score,
            score_max=score_test.score_max,
            criterion=score_test.criteria,
        )

        # The absolute value of the score can be lesser than score_max.
        score_test.score = -1
        score_test.validate_score_max(
            score=score_test.score,
            score_max=score_test.score_max,
            criterion=score_test.criteria,
        )

        score_max_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=5,
            score_max=None,
        )

        # score_max cannot be None.
        with self.assertRaises(TypeError):
            score_max_test.validate_score_max(
                score=score_max_test.score,
                score_max=score_max_test.score_max,
                criterion=score_max_test.criteria,
            )

        score_max_test.score_max = 0
        # score_max cannot be zero.
        with self.assertRaises(ValueError):
            score_max_test.validate_score_max(
                score=score_max_test.score,
                score_max=score_max_test.score_max,
                criterion=score_max_test.criteria,
            )

        score_max_test.score_max = -10
        # score_max cannot be negative.
        with self.assertRaises(ValueError):
            score_max_test.validate_score_max(
                score=score_max_test.score,
                score_max=score_max_test.score_max,
                criterion=score_max_test.criteria,
            )

        score_max_test.score_max = 10
        score_max_test.validate_score_max(
            score=score_max_test.score,
            score_max=score_max_test.score_max,
            criterion=score_max_test.criteria,
        )

    def test_clean_calls_validate_score_max(self):
        """
        The method `clean` should call the method `validate_score_max` and
        transform its exceptions into `ValidationError`.
        """
        score = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=10,
            score_max=10,
        )

        score.validate_score_max = Mock()
        score.clean()
        score.validate_score_max.assert_called_once()

        # The exceptions raised by validate_score_max should be transformed
        # into `ValidationError` by the method `clean`.
        expected_exceptions = [TypeError("oops"), ValueError("oops")]
        for exception in expected_exceptions:
            score.validate_score_max = Mock(side_effect=exception)

            with self.assertRaises(ValidationError):
                score.clean()

        # All other exceptions should not be transformed.
        score.validate_score_max = Mock(side_effect=KeyError)
        with self.assertRaises(KeyError):
            score.clean()

    def test_save_calls_validate_score_max(self):
        """
        The method `save` should call the method `validate_score_max`.
        """
        score = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=10,
            score_max=10,
        )

        score.validate_score_max = Mock()
        score.save()
        score.validate_score_max.assert_called_once()

        # All exceptions raised by validate_score_max should not be
        # transformed by `save`.
        expected_exceptions = [KeyError, TypeError, ValueError]
        for exception in expected_exceptions:
            score.validate_score_max = Mock(side_effect=exception)

            with self.assertRaises(exception):
                score.save()
