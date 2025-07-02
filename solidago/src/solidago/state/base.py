""" To use Solidago in other systems, this class should be derived to specify result storage """

from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame

import json
import pandas as pd
import logging

logger = logging.getLogger(__name__)

from .users import Users
from .vouches import Vouches
from .entities import Entities
from .made_public import MadePublic
from .assessments import Assessments
from .comparisons import Comparisons
from .voting_rights import VotingRights
from .models import ScoringModel, UserModels


class State:
    users_filename = "users.csv"
    user_scalings_filename = "user_scalings.csv"
    user_direct_scores_filename = "user_direct_scores.csv"
    global_scalings_filename = "global_scalings.csv"
    global_direct_scores_filename = "global_direct_scores.csv"
    
    def __init__(self,
        users: Optional[Users]=None,
        entities: Optional[Entities]=None,
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
        self.vouches = Vouches() if vouches is None else vouches
        self.made_public = MadePublic() if made_public is None else made_public
        self.assessments = Assessments() if assessments is None else assessments
        self.comparisons = Comparisons() if comparisons is None else comparisons
        self.voting_rights = VotingRights() if voting_rights is None else voting_rights
        self.user_models = UserModels() if user_models is None else user_models
        self.global_model = ScoringModel() if global_model is None else global_model
    
    @classmethod
    def load(cls, directory: Union[Path, str]) -> "State":
        path = Path(directory)
        with open(path / "state.json") as f: 
            j = json.load(f)
        state = cls()
        import solidago.state
        for key, j_value in j.items():
            assert hasattr(state, key)
            if j_value[0] == "Users":
                from solidago.primitives.datastructure.multi_key_array import Users as Users2
                value = Users2.load(directory, **j_value[1])
            elif j_value[0] == "Vouches":
                from solidago.primitives.datastructure.multi_key_array import Vouches as Vouches2
                value = Vouches2.load(directory, **j_value[1])
            else:
                value = getattr(solidago.state, j_value[0]).load(directory, **j_value[1])
            setattr(state, key, value)
        return state
    
    def save(self, directory: Optional[str]=None) -> tuple:
        """ Returns instructions to load content (but which is also already saved) """
        if directory is not None:
            Path(directory).mkdir(parents=True, exist_ok=True)
        self.save_instructions(directory)
        return { key: value.save(directory) for key, value in self.__dict__.items() }
    
    def save_instructions(self, directory: Optional[str]=None) -> tuple[str, dict]:
        instructions = { key: value.save_instructions() for key, value in self.__dict__.items() }
        if directory is not None:
            with open(Path(directory) / "state.json", "w") as f:
                json.dump(instructions, f, indent=4)
        return instructions

    def save_objects(self, types: type, directory: str) -> Union[list, tuple]:
        if directory is not None:
            Path(directory).mkdir(parents=True, exist_ok=True)
        if types == State:
            logger.info(f"Saving full state")
            return self.save(directory)
        if hasattr(types, "__args__"):
            return [ self.save_objects(t, directory) for t in types.__args__ ]
        state_json_filename = Path(directory) / "state.json"
        if state_json_filename.is_file():
            with open(state_json_filename) as f:
                state_json = json.load(f)
        else:
            state_json = self.save()
        for key, value in self.__init__.__annotations__.items():
            if issubclass(types, value) and getattr(self, key) is not None:
                logger.info(f"Saving state's {key}")
                state_json[key] = getattr(self, key).save(directory)
        with open(Path(directory) / "state.json", "w") as f:
            json.dump(state_json, f, indent=4)
        return state_json
    
    def copy(self):
        return State(**{ 
            key: value for key, value in self.__dict__.items() 
            if key[0] != "_" and hasattr(value, "save")
        })

    def __repr__(self) -> str:
        length = lambda value: f", with len = {len(value)}" if hasattr(value, "__len__") else ""
        return type(self).__name__ + "(\n\t" + "\n\t".join([
            f"{key}: {type(value).__name__}{length(value)}"
            for key, value in self.__dict__.items() if key[0] != "_" and hasattr(value, "save")
        ]) + "\n)"
