""" This defines the class State, which contains all updatable information by the pipeline. """

from typing import optional
from .users import Users
from .vouches import Vouches
from .entities import Entities
from .privacy import Privacy
from .judgments import Judgments
from .voting_rights import VotingRights
from .scoring_models import ScoringModel

class State:
    def __init__(
        self,
        users: Optional[Users] = None,
        vouches: Optional[Vouches] = None,
        entities: Optional[Entities] = None,
        privacy: Optional[PrivacySettings] = None,
        judgments: Optional[Judgments] = None,
        voting_rights: Optional[VotingRights] = None,
        user_models : Optional[dict[int, ScoringModel]] = None,
        global_model: Optional[ScoringModel] = None,
    ):
        self.users = users
        self.vouches = vouches
        self.entities = entities
        self.privacy = privacy
        self.judgments = judgments
        self.voting_rights = voting_rights
        self.user_models = user_models
        self.global_model = global_model

