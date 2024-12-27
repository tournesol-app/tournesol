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
        users: Users=Users(),
        vouches: Vouches=Vouches(),
        entities: Entities=Entities(),
        criteria: Criteria=Criteria(),
        made_public: MadePublic=MadePublic(),
        assessments: Assessments=Assessments(),
        comparisons: Comparisons=Comparisons(),
        voting_rights: VotingRights=VotingRights(),
        user_models : UserModels=UserModels(),
        global_model: ScoringModel=DirectScoring(),
        save_directory: Union[str, bool]=False
    ):
        """ State contains all information being processed by the pipeline 
        save_directory == False means that no save operation will be performed
        """
        self.users = users
        self.vouches = vouches
        self.entities = entities
        self.criteria = criteria
        self.made_public = made_public
        self.assessments = assessments
        self.comparisons = comparisons
        self.voting_rights = voting_rights
        self.user_models = user_models
        self.global_model = global_model
        self._save_directory = save_directory
    
    @classmethod
    def load(cls, directory: Union[Path, str]) -> "State":
        import solidago.state
        from solidago.state import Score
        path = Path(directory)
        with open(path / "state.json") as f: 
            j = json.load(f)
        def load_csv(name):
            return pd.read_csv(path / name, keep_default_na=False)
        user_scalings_df = load_csv(cls.user_scalings_filename)
        user_direct_scores_df = load_csv(cls.user_direct_scores_filename)
        global_scalings_df = load_csv(cls.global_scalings_filename)
        global_direct_scores_df = load_csv(cls.global_direct_scores_filename)
        global_scalings = dict()
        for _, r in global_scalings_df.iterrows():
            if r["depth"] not in global_scalings:
                global_scalings[r["depth"]] = dict()
            global_scalings[r["depth"]][r["criterion_id"]] = Score(r["score"], r["left_unc"], r["right_unc"])
        state = cls()
        for key, value in j.items():
            assert hasattr(state, key)
            kwargs = dict()
            if key == "user_models":
                kwargs = dict(direct_scores=user_direct_scores_df, scalings_df=user_scalings_df)
            if key == "global_model":
                kwargs = dict(direct_scores=global_direct_scores_df, scalings=global_scalings)
            setattr(state, key, getattr(solidago.state, value[0]).load(value[1], **kwargs))
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
        self.save_user_scalings()
        self.save_user_direct_scores()
        self.save_global_scalings()
        self.save_global_direct_scores()
        instructions = dict()
        for key, value in self.__dict__.items():
            if key[0] != "_" and hasattr(value, "save"):
                instructions[key] = value.save(self.save_directory)
        with open(self.save_directory / "state.json", "w") as f:
            json.dump(instructions, f, indent=4)
        return instructions

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

