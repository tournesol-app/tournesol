import solidago


class UserModels(solidago.UserModels):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
