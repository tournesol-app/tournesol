from typing import List

from django.db import models
from django.utils.functional import cached_property

from .entity import Entity

DEFAULT_POLL_NAME = "videos"


class Poll(models.Model):
    """
    A poll is an instance that enables comparing a set of "entities"
    according to some "criterias".
    """

    name = models.SlugField(unique=True)
    entity_type = models.CharField(max_length=32, choices=Entity.ENTITY_TYPE)
    criterias = models.ManyToManyField("Criteria", through="CriteriaRank")

    @classmethod
    def default_poll(cls) -> "Poll":
        poll, _created = cls.objects.get_or_create(
            name=DEFAULT_POLL_NAME,
            defaults={"entity_type": Entity.TYPE_VIDEO}
        )
        return poll

    @classmethod
    def default_poll_pk(cls):
        return cls.default_poll().pk

    @cached_property
    def criterias_list(self) -> List[str]:
        return list(self.criterias.values_list("name", flat=True))

    def __str__(self) -> str:
        return f'Poll "{self.name}"'
