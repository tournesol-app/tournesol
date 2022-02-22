from abc import ABC, abstractmethod
from functools import cache
from typing import Type

from django.utils.functional import cached_property
from rest_framework.serializers import Serializer


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

    @cached_property
    def validated_metadata(self):
        serializer = self.metadata_serializer_class(self.instance.metadata)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_metadata
