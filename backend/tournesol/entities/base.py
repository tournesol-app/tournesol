from abc import ABC, abstractmethod
from typing import Type
from rest_framework.serializers import Serializer


class EntityType(ABC):

    # The 'name' of this entity type corresponds
    # to the `type` field in Entity,
    # and to the `entity_type` in Poll.
    name: str

    metadata_serializer_class: Type[Serializer]

    @classmethod
    def filter_date_lte(cls, qs, dt):
        return qs.filter(add_time__lte=dt)

    @classmethod
    def filter_date_gte(cls, qs, dt):
        return qs.filter(add_time__gte=dt)

    @abstractmethod
    @classmethod
    def filter_search(cls, qs, query: str):
        raise NotImplementedError
