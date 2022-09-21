import logging
from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Type

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer

from tournesol import models

UID_DELIMITER = ":"


class EntityType(ABC):
    """
    Abstract base class for the processing specific to each entity type (mainly about metadata).
    """

    # The 'name' of this entity type corresponds
    # to the `type` field in Entity,
    # and to the `entity_type` in Poll.
    name: str
    metadata_serializer_class: Type[Serializer]

    # Configuration related to the metadata filter, that can be overridden by
    # child classes.

    # Allows API consumers to ask for these functions to be called on the
    # filtered value.
    metadata_allowed_filter_func = {"int": int, "str": str}
    # Allows API consumers to use these Django's field lookups on the filtered
    # field.
    metadata_allowed_filter_lookups = ["gt", "gte", "lt", "lte"]
    # This symbol delimits the field:lookup:func in the metadata filter
    # operation string.
    metadata_filter_operation_delimiter = ":"

    def __init__(self, entity: "models.Entity"):
        self.instance = entity

    @classmethod
    def validate_meta_filter_field(cls, field: str) -> None:
        """
        Raise `ValidationError` if `field` is invalid.

        A field is considered invalid if it contains the special string "__".
        This string is used by the Django's ORM to follow foreign keys, to
        navigate through fields' sub-properties and to invoke field lookups.

        Forbidding its usage prevents the users to trigger unexpected Django's
        ORM features, time-consuming or CPU heavy operations.
        """
        if "__" in field:
            # fmt: off
            raise ValidationError({
                "_url_metadata":
                    f'The metatada field `{field}` cannot contain the special string "__".'
            })
            # fmt: on

    @classmethod
    def get_allowed_meta_filter_funcs(cls) -> Dict:
        """
        Return a `dict` representing functions allowed in the metadata filter.

        The keys are arbitrary strings representing the desired function, and
        the value their matching callable.
        """
        return cls.metadata_allowed_filter_func

    @classmethod
    def get_allowed_meta_filter_lookups(cls) -> List[str]:
        """
        Return a `list` of lookups allowed in the metadata filter.

        The values must match the Django field lookups, see:
            https://docs.djangoproject.com/en/4.0/ref/models/querysets/#field-lookups-1
        """
        return cls.metadata_allowed_filter_lookups

    @classmethod
    def _get_meta_filter_func(cls, asked_func: str):
        """
        If `asked_func` is present in the allowed metadata filter functions,
        return the matching callable, return `None` instead.
        """
        allowed_funcs = cls.get_allowed_meta_filter_funcs()

        return allowed_funcs.get(asked_func)

    @classmethod
    def cast_meta_filter_value(cls, value, asked_func):
        """
        If `asked_func` is present in the allowed metadata filter functions,
        call it with value as a positional argument and return the result.
        """
        func = cls._get_meta_filter_func(asked_func)

        if func:
            return func(value)
        return value

    @classmethod
    def get_meta_filter_operation(cls, operation: str) -> Iterable[str]:
        """
        Return a field, its potential lookup, and its potential cast function
        from an `operation` string.

        The `operation` string must follow the standard:

            "{field}:{lookup}:{func}"

        Where:
            - {field} is the field on which the filter is applied
            - {lookup} is the optional Django field lookup applied to the field
            - {func} is the optional function to apply on the filtered value

        Ex 1:

            get_filter_operation("duration")

            This operation will filter entities having a metadata duration
            exactly equal to the provided string value.

        Ex 2:

            get_filter_operation("duration:lte:int")

            This operation will filter entities having a metadata duration
            inferior or equal to the provided integer value.

        Ex 3

            get_filter_operation("duration::int")

            This operation will filter entities having a metadata duration
            exactly equal to the provided integer value.
        """
        split_op = operation.split(cls.metadata_filter_operation_delimiter)

        field = split_op[0]
        lookup = None
        func = None

        if len(split_op) > 1:
            lookup = split_op[1]

        if len(split_op) > 2:
            func = split_op[2]

        return field, lookup, func

    @classmethod
    def filter_metadata(cls, qst, filters):
        for operation, values in filters:

            field, lookup, func = cls.get_meta_filter_operation(operation)
            cls.validate_meta_filter_field(field)

            if len(values) > 1:
                qst = qst.filter(**{"metadata__" + field + "__in": values})
            else:
                qstring = field

                # The lookup must be explicitly allowed to be applied.
                if lookup and lookup in cls.get_allowed_meta_filter_lookups():
                    qstring += f"__{lookup}"

                filtered_value = values[0]
                # The function must be explicitly allowed to be applied.
                if func:
                    filtered_value = cls.cast_meta_filter_value(filtered_value, func)

                qst = qst.filter(**{"metadata__" + qstring: filtered_value})

        return qst

    @classmethod
    def filter_date_lte(cls, qs, max_date):
        return qs.filter(add_time__lte=max_date)

    @classmethod
    def filter_date_gte(cls, qs, min_date):
        return qs.filter(add_time__gte=min_date)

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
            # Let's update 'last_metadata_request_at' as soon as possible,
            # to avoid repeated metadata refreshes, due to concurrent requests
            # or unexpected errors in the refresh process.
            self.instance.save(update_fields=["last_metadata_request_at"])

        self.update_metadata_field()
        # Ensure that the metadata format is valid after refresh
        self.instance.metadata = self.cleaned_metadata
        self.instance.metadata_timestamp = timezone.now()
        if save:
            self.instance.save(update_fields=["metadata", "metadata_timestamp"])

    @classmethod
    def filter_search(cls, qs, text_to_search: str, languages=None):
        """
        Filter the queryset by verifying if the text string appears in the search vector.
        The search vector contains the searchable words already filtered, stemmed and indexed
        according to each language search config.

        Postgres returns a ranking between 0 and 1 of the entities, based on how many
        times it appears and on which part of the metadata (e.g. finding
        it in the title will return a higher ranking than finding it in the
        description). The queryset is annotated with this ranking, that we call
        "relevance".

        It is currently implemented based on the PostgreSQL full-text search.
        If there is someday a need for high performances, we could
        switch to ElasticSearch. But this would require managing a
        specific server (and thus a new container).
        """
        search_query = SearchQuery(text_to_search, config=F("search_config_name"))
        qs = qs.filter_with_text_query(text_to_search, languages)
        qs = qs.alias(relevance=SearchRank(F("search_vector"), search_query))
        return qs

    @classmethod
    @abstractmethod
    def update_search_vector(cls, entity) -> None:
        raise NotImplementedError

    @staticmethod
    def build_all_search_vectors() -> None:
        """
        Rebuild the search vectors for all entities.

        This can take dozens of seconds and is usually not necessary
        because search_vector is automatically updated after a save.
        """
        # pylint: disable=import-outside-toplevel
        from tournesol.entities import ENTITY_TYPE_NAME_TO_CLASS

        for entity in models.Entity.objects.iterator():
            ENTITY_TYPE_NAME_TO_CLASS[entity.type].update_search_vector(entity)
