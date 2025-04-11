import solidago


class VotingRights(solidago.VotingRights):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
