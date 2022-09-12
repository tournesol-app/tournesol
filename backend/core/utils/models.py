"""
Utils methods for Tournesol's core app
"""

import base64
import logging
import pickle
from functools import reduce

import numpy as np
from computed_property.fields import ComputedField
from django.db.models import JSONField


def enum_list(*lst):
    """Create choices=... for a list."""
    return zip(lst, lst)


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


class WithEmbedding:
    """Define embedding setters and getters."""

    _EMBEDDING_FIELD = "embedding"

    def set_embedding(self, np_array):
        """Set embedding from an np array."""
        if np_array.shape != (self.EMBEDDING_LEN,):
            # TODO : Create a dedicated exception class to have the possibility
            #        to try/except it with ease.
            raise AssertionError("Wrong shape")
        np_bytes = pickle.dumps(np_array)
        emb_encoded = base64.b64encode(np_bytes)
        setattr(self, self._EMBEDDING_FIELD, emb_encoded)

    def get_embedding_np_array(self):
        """Get embedding as an np array."""
        try:
            decoded = base64.b64decode(getattr(self, self._EMBEDDING_FIELD))
            array = pickle.loads(decoded)
        except Exception:  # pylint: disable=broad-except
            return None
        if not isinstance(array, np.ndarray):
            return None
        if array.shape != (self.EMBEDDING_LEN,):
            # TODO : see above for dedicated class
            raise AssertionError()
        return array

    @property
    def embedding_np(self):
        """Get np array with the video embedding."""
        return self.get_embedding_np_array()

    EMBEDDING_LEN = 1536


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
