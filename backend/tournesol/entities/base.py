import logging
from abc import ABC, abstractmethod
from typing import Type

from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework.serializers import Serializer

from tournesol import models

UID_DELIMITER = ":"


class EntityType(ABC):

    # The 'name' of this entity type corresponds
    # to the `type` field in Entity,
    # and to the `entity_type` in Poll.
    name: str
    metadata_serializer_class: Type[Serializer]

    def __init__(self, entity: "models.Entity"):
        self.instance = entity

    @classmethod
    def filter_date_lte(cls, qs, dt):
        return qs.filter(add_time__lte=dt)

    @classmethod
    def filter_date_gte(cls, qs, dt):
        return qs.filter(add_time__gte=dt)

    @classmethod
    def filter_metadata(cls, qst, filters):
        for key, values in filters:
            if len(values) > 1:
                qst = qst.filter(**{"metadata__" + key + "__in": values})
            else:
                qst = qst.filter(**{"metadata__" + key: values[0]})

        return qst

    @classmethod
    @abstractmethod
    def filter_duration_lte(cls, qs, duration):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def filter_duration_gte(cls, qs, duration):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def filter_search(cls, qs, query: str):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_uid_regex(cls, namespace: str) -> str:
        """Get a regex able to validate the entity UID."""
        raise NotImplementedError

    @cached_property
    def validated_metadata(self):
        serializer = self.metadata_serializer_class(data=self.instance.metadata)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @property
    def cleaned_metadata(self):
        serializer = self.metadata_serializer_class(data=self.instance.metadata)
        serializer.is_valid(raise_exception=True)
        return serializer.data

    def metadata_needs_to_be_refreshed(self) -> bool:
        return False

    def update_metadata_field(self) -> None:
        raise NotImplementedError

    def refresh_metadata(self, *, force=False, save=True):
        if not force and not self.metadata_needs_to_be_refreshed():
            logging.debug(
                "Not refreshing metadata for entity %s. Last attempt at %s",
                self.instance.uid,
                self.instance.last_metadata_request_at,
            )
            return

        self.instance.last_metadata_request_at = timezone.now()
        if save:
            self.instance.save(update_fields=["last_metadata_request_at"])

        self.update_metadata_field()
        # Ensure that the metadata format is valid after refresh
        self.instance.metadata = self.cleaned_metadata
        self.instance.metadata_timestamp = timezone.now()
        if save:
            self.instance.save(update_fields=["metadata", "metadata_timestamp"])
