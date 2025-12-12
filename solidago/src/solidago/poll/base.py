""" To use Solidago in other systems, this class should be derived to specify result storage """

from typing import Optional, Union
from pathlib import Path

import yaml
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


class Poll:
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
        """ Poll contains all information being processed by the pipeline 
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
    def load(cls, directory: Union[Path, str]) -> "Poll":
        with open(Path(directory) / "poll.yaml") as f: 
            kwargs = yaml.safe_load(f)
        assert isinstance(kwargs, dict)
        for key, value in kwargs.items():
            assert len(value) == 2, (key, value)
        from solidago import load
        return cls(**{
            key: load(cls, directory=directory, **cls_kwargs) 
            for key, (cls, cls_kwargs) in kwargs.items()
        })
    
    def save(self, directory: Optional[str]=None) -> tuple:
        """ Returns instructions to load content (but which is also already saved) """
        if directory is not None:
            Path(directory).mkdir(parents=True, exist_ok=True)
        self.save_instructions(directory)
        return { key: value.save(directory) for key, value in self.__dict__.items() }
    
    def save_instructions(self, directory: Optional[str]=None) -> tuple[str, dict]:
        kwargs = { key: value.save_instructions() for key, value in self.__dict__.items() }
        if directory:
            with open(Path(directory) / "poll.yaml", "w") as f:
                yaml.safe_dump(kwargs, f)
        return "Poll", kwargs

    def save_objects(self, saved_keys: list[str], directory: str):
        """ Method to save only """
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)
        assert all(hasattr(self, key) for key in saved_keys)
        for key in saved_keys:
            logger.info(f"Saving poll's {key}")
            getattr(self, key).save(directory)
    
    def copy(self):
        return Poll(**{ 
            key: value for key, value in self.__dict__.items() 
            if key[0] != "_" and hasattr(value, "save")
        })

    def __repr__(self) -> str:
        length = lambda value: f", with len = {len(value)}" if hasattr(value, "__len__") else ""
        return type(self).__name__ + "(\n\t" + "\n\t".join([
            f"{key}: {type(value).__name__}{length(value)}"
            for key, value in self.__dict__.items() if key[0] != "_" and hasattr(value, "save")
        ]) + "\n)"
