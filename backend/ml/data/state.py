from ml.data.users import Users
from ml.data.vouches import Vouches
from ml.data.entities import Entities
from ml.data.made_public import MadePublic
from ml.data.assessments import Assessments
from ml.data.comparisons import Comparisons
from ml.data.voting_rights import VotingRights
from ml.data.user_models import UserModels
from ml.data.global_model import GlobalModel

import solidago



class TournesolState(solidago.State):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def load(cls, directory: str, *args, **kwargs) -> "TournesolState":
        return cls(
            users=Users.load(directory, *args, **kwargs),
            vouches=Vouches.load(directory, *args, **kwargs),
            entities=Entities.load(directory, *args, **kwargs),
            made_public=MadePublic.load(directory, *args, **kwargs),
            assessments=Assessments.load(directory, *args, **kwargs),
            comparisons=Comparisons.load(directory, *args, **kwargs),
            voting_rights=VotingRights.load(directory, *args, **kwargs),
            user_models=UserModels.load(directory, *args, **kwargs),
            global_model=GlobalModel.load(directory, *args, **kwargs),
        )
