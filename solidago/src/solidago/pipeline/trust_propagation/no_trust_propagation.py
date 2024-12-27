from .base import TrustPropagation
from solidago.state import Users, Vouches


class NoTrustPropagation(TrustPropagation):
    def __init__(self, pretrust_value: float=0.8,):
        """
        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        self.pretrust_value = pretrust_value

    def propagate(self, users: Users, vouches: Vouches) -> Users:
        users["trust_score"] = users["is_pretrusted"] * self.pretrust_value
        return users
        
    def __str__(self):
        return f"{type(self).__name__}(pretrust_value={self.pretrust_value})"
		
    def args_save(self) -> dict[str, float]:
        return { "pretrust_value": self.pretrust_value }
