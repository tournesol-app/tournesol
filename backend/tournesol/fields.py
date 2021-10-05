from rest_framework import serializers


class RelativeFloatField(serializers.FloatField):
    """
    A DRF `FloatField` able to serialize and deserialize its original floating
    value or its relative counterpart.

    Example, initializing a `RelativeFloatField` as a classic `FloatField`.
    The value provided will be serialized/deserialized without alteration.

        class ExampleSerializer(Serializers):
            score = RelativeFloatField()

    Example, initializing a `RelativeFloatField` in reverse mode. The value
    serialized/deserialized will be the opposite of the value provided.

        class ExampleSerializer(Serializers):
            score = RelativeFloatField(reverse=True)
    """
    factor = 1

    def __init__(self, **kwargs):
        self.reverse = kwargs.pop('reverse', False)
        super().__init__(**kwargs)

        if self.reverse:
            self.factor = -1

    def to_representation(self, value):
        return self.factor * value

    def to_internal_value(self, data):
        return self.factor * data
