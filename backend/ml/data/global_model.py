import solidago


class GlobalModel(solidago.ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
