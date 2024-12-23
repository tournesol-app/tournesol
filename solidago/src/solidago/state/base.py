""" To use Solidago in other systems, this class should be derived to specify result storage """

from typing import Optional, Union
from pathlib import Path

import json
import pandas as pd

from .users.base import Users
from .vouches.base import Vouches
from .entities.base import Entities
from .privacy.base import Privacy
from .judgments.base import Judgments
from .voting_rights.base import VotingRights
from .models.direct import ScoringModel, DirectScoring
from .models.user_models import UserModels


class State:
    def __init__(
        self,
        users: Users=Users(),
        vouches: Vouches=Vouches(),
        entities: Entities=Entities(),
        privacy: Privacy=Privacy(),
        judgments: Judgments=Judgments(),
        voting_rights: VotingRights=VotingRights(),
        user_models : UserModels=UserModels(),
        global_model: ScoringModel=DirectScoring(),
        save_directory: str = "temp"
    ):
        """ State contains all information being processed by the pipeline """
        self.users = users
        self.vouches = vouches
        self.entities = entities
        self.privacy = privacy
        self.judgments = judgments
        self.voting_rights = voting_rights
        self.user_models = user_models
        self.global_model = global_model
        self._save_directory = save_directory
    
    @classmethod
    def load(cls, directory: Union[Path, str]) -> "State":
        import solidago.state
        path = Path(directory)
        with open(path / "state.json") as f: 
            j = json.load(f)
        def load_csv(name):
            try: return pd.read_csv(j[name], keep_default_na=False)
            except: return pd.DataFrame()
        user_scalings, user_direct_scores = load_csv("scalings"), load_csv("user_direct_scores")
        global_scalings, global_direct_scores = load_csv("global_scalings"), load_csv("global_direct_scores")
        state = cls()
        for key, value in j.items():
            assert hasattr(self, key)
            kwargs = dict()
            if key == "user_models":
                kwargs = dict(users=state.users, entities=state.entities, user_direct_scores=user_direct_scores, user_scalings=user_scalings)
            if key == "global_model":
                kwargs = dict(entities=state.entities, direct_scores=global_direct_scores, scalings=global_scalings)
            setattr(self, key, getattr(solidago.state, value[0])(value[1], **kwargs))
        return state
    
    @property
    def save_directory(self):
        return Path(self._save_directory)
        
    @save_directory.setter
    def save_directory(self, directory: Optional[str]=None):
        self._save_directory = self._save_directory if directory is None else directory
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
    def save(self, directory: Optional[str]=None):
        self.save_directory = directory
        self.save_trust_scores()
        self.save_user_scalings()
        self.save_user_direct_scores()
        self.save_global_scores()
        self.save_global_scalings()
        instructions = dict()
        for key, value in self.__dict__.items():
            if key[0] != "_" and hasattr(value, "save"):
                instructions[key] = value.save(self.save_directory)
        with open(self.save_directory / "state.json") as f:
            json.dump(instructions, f)
        return instructions

    def save_trust_scores(self, directory: Optional[str]=None):
        self.save_directory = directory
        self.users.to_csv(self.save_directory / "users.csv")

    def save_user_scalings(self, directory: Optional[str]=None):
        self.save_directory = directory
        return self.user_models.save_scalings(self.save_directory / "scalings.csv")

    def save_user_direct_scores(self, directory: Optional[str]=None):
        self.save_directory = directory
        return self.user_models.save_direct_scores(self.save_directory / "user_direct_scores.csv")

    def save_global_scores(self, directory: Optional[str]=None):
        self.save_directory = directory
        return self.global_model.foundational_model().save(self.save_directory / "global_direct_scores.csv")

    def save_global_scalings(self, directory: Optional[str]=None):
        self.save_directory = directory
        return self.global_model.save_scalings(self.save_directory / "global_scalings.csv")

