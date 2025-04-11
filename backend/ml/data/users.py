import solidago


class Users(solidago.Users):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
