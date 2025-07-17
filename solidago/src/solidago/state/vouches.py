from solidago.primitives.datastructures import MultiKeyArray

class Vouches(MultiKeyArray):
    KEY_NAMES = ["by", "to", "kind"]
    VALUE_NAMES = ["weight", "priority"]

