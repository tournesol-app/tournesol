import base64
import pickle
from functools import reduce
import logging

from django.db.models import JSONField

from computed_property.fields import ComputedField
import numpy as np

from settings.settings import CRITERIAS


def EnumList(*lst):
    """Create choices=... for a list."""
    return zip(lst, lst)


class WithDynamicFields(object):
    """Add dynamically-created fields to a model."""
    fields_created = False

    @staticmethod
    def _create_fields(self):
        """Override this method to create dynamic fields."""
        pass

    @staticmethod
    def create_all():
        """Create all dynamic fields for all models."""
        subclasses = WithDynamicFields.__subclasses__()
        for scl in subclasses:
            if not scl.fields_created:
                scl.fields_created = True
                scl._create_fields()


class WithFeatures(object):
    """An object containing features."""

    # subtract this value from all returned vectors
    VECTOR_OFFSET = 0.0

    def _features_as_vector_fcn(self, suffix=""):
        """Get features a vector, append suffix to field names."""

        def transform_nan(x):
            """None -> np.nan."""
            if x is None:
                return np.nan
            else:
                return x

        return np.array([transform_nan(getattr(self, f + suffix)) for f in CRITERIAS])

    @property
    def features_as_vector(self):
        """Get features a vector."""
        return self._features_as_vector_fcn()

    @property
    def features_as_vector_centered(self):
        """Get features as a vector, center around self.VECTOR_OFFSET"""
        return self.features_as_vector - self.VECTOR_OFFSET


class WithEmbedding(object):
    """Define embedding setters and getters."""
    _EMBEDDING_FIELD = 'embedding'

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
        except BaseException:
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
    pass


def filter_reduce(lst, fcn, name='_'):
    """Reduce a list of filters."""
    lst_orig = lst
    lst = [x for x in lst if x is not None]
    if not lst:
        logging.warning(f"{name} query with en empty list of operands, returning None: {lst_orig}")
        return None
    return reduce(fcn, lst)


def query_or(lst):
    """Combine query parts with OR."""
    return filter_reduce(lst, fcn=(lambda x, y: x | y),
                         name='OR')


def query_and(lst):
    """Combine query parts with AND."""
    return filter_reduce(lst, fcn=(lambda x, y: x & y),
                         name='AND')
