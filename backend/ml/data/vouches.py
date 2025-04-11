import solidago


class Vouches(solidago.Vouches):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
