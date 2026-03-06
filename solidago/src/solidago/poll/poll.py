""" To use Solidago in other systems, this class should be derived to specify result storage """

from pathlib import Path
from typing import Any

import yaml
import logging

logger = logging.getLogger(__name__)

from .poll_tables import *
from .scoring import ScoringModel, UserModels


class Poll:
    users_filename = "users.csv"
    user_scalings_filename = "user_scalings.csv"
    user_direct_scores_filename = "user_direct_scores.csv"
    global_scalings_filename = "global_scalings.csv"
    global_direct_scores_filename = "global_direct_scores.csv"

    types: dict[str, type] = dict(
        users=Users, entities=Entities, socials=Socials, public_settings=PublicSettings,
        ratings=Ratings, comparisons=Comparisons, voting_rights=VotingRights,
        user_models=UserModels, global_model=ScoringModel,
        past_recommendations=PastRecommendations,
    )
    
    def __init__(self,
        users: Users | None = None,
        entities: Entities | None = None,
        socials: Socials | None = None,
        public_settings: PublicSettings | None = None,
        ratings: Ratings | None = None,
        comparisons: Comparisons | None = None,
        voting_rights: VotingRights | None = None,
        user_models : UserModels | None = None,
        global_model: ScoringModel | None = None,
        past_recommendations: PastRecommendations | None = None,
    ):
        """ Poll contains all information being processed by the pipeline 
        save_directory == False means that no save operation will be performed
        """
        self.users = Users() if users is None else users
        self.entities = Entities() if entities is None else entities
        self.socials = Socials() if socials is None else socials
        self.public_settings = PublicSettings() if public_settings is None else public_settings
        self.ratings = Ratings() if ratings is None else ratings
        self.comparisons = Comparisons() if comparisons is None else comparisons
        self.voting_rights = VotingRights() if voting_rights is None else voting_rights
        self.user_models = UserModels() if user_models is None else user_models
        self.global_model = ScoringModel() if global_model is None else global_model
        self.past_recommendations = PastRecommendations() if past_recommendations is None else past_recommendations
        for name, t in self.types.items():
            assert isinstance(getattr(self, name), t), (name, getattr(self, name), t)

    @classmethod
    def key_by_type(cls, value: Any) -> str:
        for name, type in cls.types.items():
            if isinstance(value, type):
                return name
        raise ValueError(f"{value} does not have the type of a poll attribute")
    
    def criteria(self) -> set[str]:
        criteria = self.ratings.keys("criterion")
        criteria |= self.comparisons.keys("criterion")
        criteria |= self.voting_rights.keys("criterion")
        criteria |= self.user_models.criteria()
        criteria |= self.global_model.criteria()
        return criteria # type: ignore

    @classmethod
    def load(cls, directory: Path | str | None = None, **kwargs: Any) -> "Poll":
        if directory is None:
            return cls(**kwargs)
        path = Path(directory) / "poll.yaml"
        assert path.is_file(), f"Failed to load {path}. File does not exist."
        kwargs = dict(
            users=(Users, dict()), 
            entities=(Entities, dict()), 
            socials=(Socials, dict()), 
            public_settings=(PublicSettings, dict()),
            ratings=(Ratings, dict()), 
            comparisons=(Comparisons, dict()),
            voting_rights=(VotingRights, dict()),
            user_models=("UserModels", dict()),
            global_model=("ScoringModel", dict()),
            past_recommendations=(PastRecommendations, dict())
        ) | kwargs
        with open(Path(directory) / "poll.yaml") as f: 
            kwargs |= yaml.safe_load(f)

        import solidago.poll as poll
        clsname, cls_kwargs = kwargs["user_models"]
        user_models = getattr(poll, clsname).load_tables(directory, **cls_kwargs)
        clsname, cls_kwargs = kwargs["global_model"]
        global_model = getattr(poll, clsname).load_tables(directory, filename="global", **cls_kwargs)
        
        from solidago import load
        poll_kwargs = {
            key: load(subcls, directory=directory, **subcls_kwargs) 
            for key, (subcls, subcls_kwargs) in kwargs.items()
            if key not in {"user_models", "global_model"}
        }

        return cls(**(poll_kwargs | dict(user_models=user_models, global_model=global_model))) # type: ignore
    
    def save(self, directory: str | Path, save_instructions: bool = True) -> tuple:
        """ Returns instructions to load content (but which is also already saved) """
        assert isinstance(directory, (str, Path))
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.users.save(directory)
        self.entities.save(directory)
        self.socials.save(directory)
        self.public_settings.save(directory)
        self.ratings.save(directory)
        self.comparisons.save(directory)
        self.voting_rights.save(directory)
        self.user_models.save(directory, False)
        self.global_model.save(directory, "global", save_instructions=False)
        self.past_recommendations.save(directory)
        return self.save_instructions(directory if save_instructions else None)
    
    def save_instructions(self, directory: str | Path | None = None) -> tuple[str, dict]:
        kwargs = { 
            key: value.save_instructions() 
            for key, value in self.__dict__.items() 
            if value.requires_save_instructions()
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
                if value.requires_save_instructions():
                    poll_yaml[key] = instruction # type: ignore
        
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
