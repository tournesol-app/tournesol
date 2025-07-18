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
    Users: type=Users
    Vouches: type=Vouches
    Entities: type=Entities
    MadePublic: type=MadePublic
    Assessments: type=Assessments
    Comparisons: type=Comparisons
    VotingRights: type=VotingRights
    UserModels: type=UserModels
    GlobalModel: type=GlobalModel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def load(cls, poll_name: str, *args, **kwargs) -> "TournesolState":
        return cls(
            users=Users.load(poll_name, *args, **kwargs),
            vouches=Vouches.load(poll_name, *args, **kwargs),
            entities=Entities.load(poll_name, *args, **kwargs),
            made_public=MadePublic.load(poll_name, *args, **kwargs),
            assessments=Assessments.load(poll_name, *args, **kwargs),
            comparisons=Comparisons.load(poll_name, *args, **kwargs),
            voting_rights=VotingRights.load(poll_name, *args, **kwargs),
            user_models=UserModels.load(poll_name, *args, **kwargs),
            global_model=GlobalModel.load(poll_name, *args, **kwargs),
        )
