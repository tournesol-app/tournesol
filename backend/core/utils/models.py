"""
Utils methods for Tournesol's core app
"""

import logging
from functools import reduce

from computed_property.fields import ComputedField
from django.db.models import JSONField


class WithDynamicFields:
    """Add dynamically-created fields to a model."""

    fields_created = False

    @staticmethod
    def create_fields():
        """Override this method to create dynamic fields."""

    @staticmethod
    def create_all():
        """Create all dynamic fields for all models."""
        subclasses = WithDynamicFields.__subclasses__()
        for scl in subclasses:
            if not scl.fields_created:
                scl.fields_created = True
                scl.create_fields()


class ComputedJsonField(ComputedField, JSONField):
    """A JSON field that is computed from other fields."""


def filter_reduce(lst, fcn, name="_"):
    """Reduce a list of filters."""
    lst_orig = lst
    lst = [x for x in lst if x is not None]
    if not lst:
        logging.warning(
            "%s query returned None due to an empty list of operands: %s", name, lst_orig
        )
        return None
    return reduce(fcn, lst)


def query_or(lst):
    """Combine query parts with OR."""
    return filter_reduce(lst, fcn=(lambda x, y: x | y), name="OR")


def query_and(lst):
    """Combine query parts with AND."""
    return filter_reduce(lst, fcn=(lambda x, y: x & y), name="AND")
