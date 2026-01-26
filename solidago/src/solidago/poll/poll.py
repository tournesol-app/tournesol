""" To use Solidago in other systems, this class should be derived to specify result storage """

from pathlib import Path

import yaml
import logging

logger = logging.getLogger(__name__)

from .users import Users
from .vouches import Vouches
from .entities import Entities
from .made_public import MadePublic
from .ratings import Ratings
from .comparisons import Comparisons
from .voting_rights import VotingRights
from .scoring import ScoringModel, UserModels


class Poll:
    users_filename = "users.csv"
    user_scalings_filename = "user_scalings.csv"
    user_direct_scores_filename = "user_direct_scores.csv"
    global_scalings_filename = "global_scalings.csv"
    global_direct_scores_filename = "global_direct_scores.csv"
    
    def __init__(self,
        users: Users | None = None,
        entities: Entities | None = None,
        vouches: Vouches | None = None,
        made_public: MadePublic | None = None,
        ratings: Ratings | None = None,
        comparisons: Comparisons | None = None,
        voting_rights: VotingRights | None = None,
        user_models : UserModels | None = None,
        global_model: ScoringModel | None = None,
    ):
        """ Poll contains all information being processed by the pipeline 
        save_directory == False means that no save operation will be performed
        """
        self.users = Users() if users is None else users
        self.entities = Entities() if entities is None else entities
        self.vouches = Vouches() if vouches is None else vouches
        self.made_public = MadePublic() if made_public is None else made_public
        self.ratings = Ratings() if ratings is None else ratings
        self.comparisons = Comparisons() if comparisons is None else comparisons
        self.voting_rights = VotingRights() if voting_rights is None else voting_rights
        self.user_models = UserModels() if user_models is None else user_models
        self.global_model = ScoringModel() if global_model is None else global_model
    
    def key_by_type(value) -> str:
        types = dict(users=Users, entities=Entities, vouches=Vouches, made_public=MadePublic)
        types |= dict(ratings=Ratings, comparisons=Comparisons, voting_rights=VotingRights)
        types |= dict(user_models=UserModels, global_model=ScoringModel)
        for name, type in types.items():
            if isinstance(value, type):
                return name
        raise ValueError(f"{value} does not have the type of a poll attribute")
    
    def criteria(self) -> set[str]:
        criteria = self.ratings.keys("criterion") 
        criteria |= self.comparisons.keys("criterion") 
        criteria |= self.voting_rights.keys("criterion") 
        criteria |= self.user_models.criteria() 
        criteria |= self.global_model.criteria()
        return criteria

    @classmethod
    def load(cls, directory: Path | str | None = None, **kwargs) -> "Poll":
        if directory is None:
            return cls(**kwargs)
        path = Path(directory) / "poll.yaml"
        assert path.is_file(), f"Failed to load {path}. File does not exist."
        kwargs = dict(
            users=(Users, dict()), 
            entities=(Entities, dict()), 
            vouches=(Vouches, dict()), 
            made_public=(MadePublic, dict()),
            ratings=(Ratings, dict()), 
            comparisons=(Comparisons, dict()),
            voting_rights=(VotingRights, dict()),
            user_models=(UserModels, dict()),
            global_model=(ScoringModel, dict()),
        ) | kwargs
        with open(Path(directory) / "poll.yaml") as f: 
            kwargs |= yaml.safe_load(f)

        import solidago.poll as poll
        clsname, cls_kwargs = kwargs["user_models"]
        user_models = getattr(poll, clsname).load_tables(directory, **cls_kwargs)
        clsname, cls_kwargs = kwargs["global_model"]
        global_model = getattr(poll, clsname).load_tables(directory, filename="global", **cls_kwargs)
        
        from solidago import load
        return cls(**{
            key: load(subcls, directory=directory, **subcls_kwargs) 
            for key, (subcls, subcls_kwargs) in kwargs.items()
            if key not in {"user_models", "global_model"}
        } | dict(user_models=user_models, global_model=global_model))
    
    def save(self, directory: str | Path, save_instructions: bool = True) -> tuple:
        """ Returns instructions to load content (but which is also already saved) """
        assert isinstance(directory, (str, Path))
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.users.save(directory)
        self.entities.save(directory)
        self.vouches.save(directory)
        self.made_public.save(directory)
        self.ratings.save(directory)
        self.comparisons.save(directory)
        self.voting_rights.save(directory)
        self.user_models.save(directory, False)
        self.global_model.save(directory, "global", save_instructions=False)
        return self.save_instructions(directory if save_instructions else None)
    
    def save_instructions(self, directory: str | None = None) -> tuple[str, dict]:
        kwargs = { 
            key: value.save_instructions() 
            for key, value in self.__dict__.items() 
            if not value.has_default_type()
        }
        if directory:
            with open(Path(directory) / "poll.yaml", "w") as f:
                yaml.safe_dump(kwargs, f)
        return "Poll", kwargs
    
    def save_objects(self, types: type, directory: str | Path) -> list | tuple:
        assert isinstance(directory, (str, Path))
        
        Path(directory).mkdir(parents=True, exist_ok=True)
        if types == Poll:
            return self.save(directory)
        if hasattr(types, "__args__"):
            return [ self.save_objects(t, directory) for t in types.__args__ ]
        
        poll_filename = Path(directory) / "poll.yaml"
        if poll_filename.is_file():
            with open(poll_filename) as f:
                poll_yaml = yaml.safe_load(f)
        else:
            poll_yaml = self.save(directory)
        
        for key, key_type in self.__init__.__annotations__.items():
            if issubclass(types, key_type) and getattr(self, key) is not None:
                value = getattr(self, key)
                assert isinstance(value, key_type), (value, key_type)
                instruction = value.save(directory, save_instructions=False)
                if not value.has_default_type():
                    poll_yaml[key] = instruction
        
        with open(Path(directory) / "poll.yaml", "w") as f:
            yaml.safe_dump(poll_yaml, f)
        
        return poll_yaml
    
    def copy(self) -> "Poll": # Not a deepcopy
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
