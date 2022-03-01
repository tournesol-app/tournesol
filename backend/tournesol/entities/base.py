from abc import ABC, abstractmethod
from typing import Type

from django.utils.functional import cached_property
from rest_framework.serializers import Serializer

UID_DELIMITER = ":"


class EntityType(ABC):

    # The 'name' of this entity type corresponds
    # to the `type` field in Entity,
    # and to the `entity_type` in Poll.
    name: str
    metadata_serializer_class: Type[Serializer]

    def __init__(self, entity):
        self.instance = entity

    @classmethod
    def filter_date_lte(cls, qs, dt):
        return qs.filter(add_time__lte=dt)

    @classmethod
    def filter_date_gte(cls, qs, dt):
        return qs.filter(add_time__gte=dt)

    @classmethod
    @abstractmethod
    def filter_search(cls, qs, query: str):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_uid_regex(cls, namespace: str):
        """Get a regex able to validate the entity UID."""
        raise NotImplementedError

    @cached_property
    def validated_metadata(self):
        serializer = self.metadata_serializer_class(data=self.instance.metadata)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
