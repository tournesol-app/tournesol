""" To use Solidago in other systems, this class should be derived to specify result storage """

from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame

import json
import pandas as pd

from .users.base import Users
from .vouches.base import Vouches
from .entities.base import Entities
from .criteria.base import Criteria
from .made_public.base import MadePublic
from .assessments.base import Assessments
from .comparisons.base import Comparisons
from .voting_rights.base import VotingRights
from .models.direct import ScoringModel, DirectScoring
from .models.user_models import UserModels


class State:
    users_filename = "users.csv"
    user_scalings_filename = "user_scalings.csv"
    user_direct_scores_filename = "user_direct_scores.csv"
    global_scalings_filename = "global_scalings.csv"
    global_direct_scores_filename = "global_direct_scores.csv"
    
    def __init__(
        self,
        users: Optional[Users]=None,
        entities: Optional[Entities]=None,
        criteria: Optional[Criteria]=None,
        vouches: Optional[Vouches]=None,
        made_public: Optional[MadePublic]=None,
        assessments: Optional[Assessments]=None,
        comparisons: Optional[Comparisons]=None,
        voting_rights: Optional[VotingRights]=None,
        user_models : Optional[UserModels]=None,
        global_model: Optional[ScoringModel]=None,
    ):
        """ State contains all information being processed by the pipeline 
        save_directory == False means that no save operation will be performed
        """
        self.users = Users() if users is None else users
        self.entities = Entities() if entities is None else entities
        self.criteria = Criteria() if criteria is None else criteria
        self.vouches = Vouches() if vouches is None else vouches
        self.made_public = MadePublic() if made_public is None else made_public
        self.assessments = Assessments() if assessments is None else assessments
        self.comparisons = Comparisons() if comparisons is None else comparisons
        self.voting_rights = VotingRights() if voting_rights is None else voting_rights
        self.user_models = UserModels() if user_models is None else user_models
        self.global_model = DirectScoring() if global_model is None else global_model
        self._save_directory = None
    
    @classmethod
    def load(cls, directory: Union[Path, str]) -> "State":
        import solidago.state
        path = Path(directory)
        with open(path / "state.json") as f: 
            j = json.load(f)
        state = cls()
        for key, j_value in j.items():
            assert hasattr(state, key)
            value = getattr(solidago.state, j_value[0]).load(j_value[1])
            setattr(state, key, value)
        return state
    
    @property
    def save_directory(self) -> Union[Path, bool]:
        return False if self._save_directory == False else Path(self._save_directory)
        
    @save_directory.setter
    def save_directory(self, directory: Optional[Union[str, Path, bool]]=None):
        self._save_directory = self._save_directory if directory is None else directory
        if isinstance(directory, (str, Path)):
            self.save_directory.mkdir(parents=True, exist_ok=True)
        
    def save(self, directory: Optional[str]=None) -> dict():
        """ Returns instructions to load content (but which is also already saved) """
        self.save_directory = directory
        if self.save_directory == False:
            return dict()
        instructions = dict()
        for key, value in self.__dict__.items():
            if key == "global_model":
                instructions[key] = value.save(Path(self.save_directory) / "global")
            elif key[0] != "_" and hasattr(value, "save"):
                instructions[key] = value.save(self.save_directory)
        with open(self.save_directory / "state.json", "w") as f:
            json.dump(instructions, f, indent=4)
        return instructions
    
    def copy(self):
        return State(**{ 
            key: value for key, value in self.__dict__.items() 
            if key[0] != "_" and hasattr(value, "save")
        })

    def save_trust_scores(self, directory: Optional[str]=None) -> None:
        self.save_directory = directory
        self.users.to_csv(self.save_directory / self.users_filename)

    def save_user_scalings(self, directory: Optional[str]=None) -> None:
        self.save_directory = directory
        return self.user_models.save_scalings(self.save_directory / self.user_scalings_filename)

    def save_user_direct_scores(self, directory: Optional[str]=None) -> None:
        self.save_directory = directory
        return self.user_models.save_direct_scores(self.save_directory / self.user_direct_scores_filename)

    def save_global_scalings(self, directory: Optional[str]=None) -> None:
        self.save_directory = directory
        return self.global_model.save_scalings(self.save_directory / self.global_scalings_filename)

    def save_global_direct_scores(self, directory: Optional[str]=None) -> None:
        self.save_directory = directory
        return self.global_model.save_direct_scores(self.save_directory / self.global_direct_scores_filename)

    def __repr__(self) -> str:
        return type(self).__name__ + "(\n\t" + "\n\t".join([
            f"{key}: {type(value).__name__}, with len = {len(value)}"
            for key, value in self.__dict__.items() if key[0] != "_" and hasattr(value, "save")
        ]) + "\n)"
