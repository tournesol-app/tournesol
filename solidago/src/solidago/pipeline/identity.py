from .sequential import Sequential


class Identity(Sequential):
    def __init__(self):
        super().__init__()
