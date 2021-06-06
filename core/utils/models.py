import numpy as np

def EnumList(*lst):
    """Create choices=... for a list."""
    return zip(lst, lst)


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