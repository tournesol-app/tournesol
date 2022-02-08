from django.db import models

from .entity import Entity

DEFAULT_POLL_NAME = "videos"


class Poll(models.Model):
    """
    A poll is an instance that enables comparing a set of "entities"
    according to some "criterias".
    """

    name = models.SlugField(unique=True)
    entity_type = models.CharField(max_length=32, choices=Entity.ENTITY_TYPE)

    @classmethod
    def default_poll_pk(cls):
        poll, _created = cls.objects.get_or_create(
            name=DEFAULT_POLL_NAME,
            defaults={"entity_type": Entity.TYPE_VIDEO}
        )
        return poll.pk

    def __str__(self) -> str:
        return f'Poll "{self.name}"'
