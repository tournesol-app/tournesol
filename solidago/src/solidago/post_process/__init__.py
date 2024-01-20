from abc import ABC, abstractmethod

from solidago.scoring_model import ScoringModel

class PostProcess(ABC):
    @abstractmethod
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        global_model: ScoringModel
    ) -> tuple[dict[int, ScoringModel], ScoringModel]:
        """ Post-processes user models and global models,
        typically to yield human-readible scores
        
        Parameters
        ----------
        user_models: user_model[user] should be a ScoringModel to post-process
        global_model: ScoringModel to post-process
        
        Returns
        -------
        user_models: post-processed user models
        global_model: post-processed global model
        """
        raise NotImplementedError
