from math import tau as TAU
from typing import List

import numpy as np
from django.core.signing import Signer
from django.db import models
from django.utils.functional import cached_property

from tournesol.entities import ENTITY_TYPE_CHOICES, ENTITY_TYPE_NAME_TO_CLASS, VideoEntity
from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE

DEFAULT_POLL_NAME = "videos"

ALGORITHM_LICCHAVI = "licchavi"
ALGORITHM_MEHESTAN = "mehestan"

ALGORITHM_CHOICES = (
    (ALGORITHM_LICCHAVI, "Licchavi"),
    (ALGORITHM_MEHESTAN, "Mehestan"),
)

PROOF_OF_VOTE_KEYWORD = "proof_of_vote"


class Poll(models.Model):
    """
    A poll is an instance that enables comparing a set of "entities"
    according to some "criterias".
    """

    name = models.SlugField(unique=True)
    entity_type = models.CharField(max_length=32, choices=ENTITY_TYPE_CHOICES)
    criterias = models.ManyToManyField("Criteria", through="CriteriaRank")
    algorithm = models.CharField(
        max_length=32, choices=ALGORITHM_CHOICES, default=ALGORITHM_MEHESTAN
    )
    active = models.BooleanField(
        default=True,
        help_text="On an inactive poll, entity scores are not updated"
        " and comparisons can't be created, updated or deleted by users.",
    )

    sigmoid_scale = models.FloatField(
        null=True,
        default=None,
        help_text="Scaling factor multiplied by score before the sigmoid function is applied."
        " Updated automatically on each run. (Mehestan only)."
    )

    def __str__(self) -> str:
        return f'Poll "{self.name}"'

    @classmethod
    def default_poll(cls) -> "Poll":
        poll, _created = cls.objects.get_or_create(
            name=DEFAULT_POLL_NAME,
            defaults={"entity_type": VideoEntity.name}
        )
        return poll

    @classmethod
    def default_poll_pk(cls):
        return cls.objects.only("pk").get(name=DEFAULT_POLL_NAME).pk

    @cached_property
    def criterias_list(self) -> List[str]:
        return list(self.criterias.values_list("name", flat=True))

    @cached_property
    def required_criterias_list(self) -> List[str]:
        return list(
            self.criterias
            .filter(criteriarank__optional=False)
            .values_list("name", flat=True)
        )

    @property
    def main_criteria(self):
        criterias = self.criterias_list
        if len(criterias) > 0:
            return criterias[0]
        return None

    @property
    def entity_cls(self):
        return ENTITY_TYPE_NAME_TO_CLASS[self.entity_type]

    @property
    def scale_function(self):
        if self.algorithm == ALGORITHM_MEHESTAN and self.sigmoid_scale is not None:
            return lambda x: (4 * MEHESTAN_MAX_SCALED_SCORE / TAU) * \
                             np.arctan(self.sigmoid_scale * x)
        return lambda x: x

    def user_meets_proof_requirements(self, user_id: int, keyword: str) -> bool:
        """
        Return False if the proof identified by the provided keyword has
        requirements not satisfied by the provided user, return True instead.

        Random keywords that are not understood by the poll will always return
        True.
        """
        from core.models.user import User  # pylint: disable=import-outside-toplevel

        from ..models import Comparison  # pylint: disable=import-outside-toplevel

        # A proof can be obtained only by activated users.
        try:
            User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return False

        # A proof of vote requires at least one comparison made.
        if keyword == PROOF_OF_VOTE_KEYWORD:
            comparisons = Comparison.objects.filter(poll=self, user_id=user_id)

            if not comparisons.exists():
                return False

        return True

    def get_user_proof(self, user_id: int, keyword: str):
        """
        Return the user_id and its signature, derived from the current poll
        name and the specified keyword.
        """
        signer = Signer(salt=f"{keyword}:{self.name}")
        return signer.sign(f"{user_id:05d}")
