"""
Models for Tournesol app
"""

from .comparisons import Comparison, ComparisonCriteriaScore
from .criteria import Criteria, CriteriaLocale, CriteriaRank
from .entity import Entity, VideoRateLater
from .entity_score import EntityCriteriaScore
from .poll import Poll
from .ratings import ContributorRating, ContributorRatingCriteriaScore
from .scaling import ContributorScaling
