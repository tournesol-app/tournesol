import base64
import pickle
from functools import reduce
import logging

import numpy as np
from backend.rating_fields import VIDEO_FIELDS
from urllib.parse import urlparse
from computed_property import ComputedField
from jsonfield import JSONField


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
        return np.array([transform_nan(getattr(self, f + suffix)) for f in VIDEO_FIELDS])

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
        assert np_array.shape == (self.EMBEDDING_LEN,), "Wrong shape"
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
        assert array.shape == (self.EMBEDDING_LEN,)
        return array

    @property
    def embedding_np(self):
        """Get np array with the video embedding."""
        return self.get_embedding_np_array()

    EMBEDDING_LEN = 1536


class WithDynamicFields(object):
    """Add dynamically-created fields to a model."""

    @staticmethod
    def _create_fields(self):
        """Override this method to create dynamic fields."""
        pass

    @staticmethod
    def create_all():
        """Create all dynamic fields for all models."""
        subclasses = WithDynamicFields.__subclasses__()
        for scl in subclasses:
            scl._create_fields()


def EnumList(*lst):
    """Create choices=... for a list."""
    return zip(lst, lst)


def url_has_domain(url, domain):
    """Check if a URL belongs to a given domain."""

    def domain_remove_www(domain_name, prefix='www.'):
        """Remove the leading www, if present."""
        if domain_name.startswith(prefix):
            domain_name = domain_name[len(prefix):]
        return domain_name

    # empty value -> valid value
    if url is None or not url:
        return True

    try:
        url_domain = str(urlparse(url).netloc)
    except ValueError:
        return False

    return domain_remove_www(domain) == domain_remove_www(url_domain)


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


class ComputedJsonField(ComputedField, JSONField):
    """A JSON field that is computed from other fields."""
    pass
