from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class Squash(PollFunction):
    def __init__(self, score_max: float = 100.0, *args, **kwargs):
        assert score_max > 0
        super().__init__(*args, **kwargs)
        self.score_max = score_max
    
    def __call__(self, 
        user_models: UserModels,
        global_model: ScoringModel,
    ) -> tuple[UserModels, ScoringModel]:
        """ Post-processes user models and global models,
        typically to yield human-readible scores, 
        by squashing scores into [-self.score_max, self.score_max] """
        user_models = user_models.post_process("Squash", max=self.score_max)
        global_model = global_model.post_process("Squash", max=self.score_max)
        return user_models, global_model

    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict]:
        return poll.save_instructions(directory)
