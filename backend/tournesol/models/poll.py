from typing import List

from django.db import models
from django.utils.functional import cached_property

from tournesol.entities import ENTITY_TYPE_CHOICES, ENTITY_TYPE_NAME_TO_CLASS, VideoEntity

DEFAULT_POLL_NAME = "videos"

ALGORITHM_LICCHAVI = "licchavi"
ALGORITHM_MEHESTAN = "mehestan"

ALGORITHM_CHOICES = (
    (ALGORITHM_LICCHAVI, "Licchavi"),
    (ALGORITHM_MEHESTAN, "Mehestan"),
)


class Poll(models.Model):
    """
    A poll is an instance that enables comparing a set of "entities"
    according to some "criterias".
    """

    name = models.SlugField(unique=True)
    entity_type = models.CharField(max_length=32, choices=ENTITY_TYPE_CHOICES)
    criterias = models.ManyToManyField("Criteria", through="CriteriaRank")
    algorithm = models.CharField(
        max_length=32, choices=ALGORITHM_CHOICES, default=ALGORITHM_LICCHAVI
    )

    # @property
    # def algorithm(self):
    #     return ALGORITHM_MEHESTAN

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
    def entity_cls(self):
        return ENTITY_TYPE_NAME_TO_CLASS[self.entity_type]

    def __str__(self) -> str:
        return f'Poll "{self.name}"'
