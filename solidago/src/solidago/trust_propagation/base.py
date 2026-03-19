from abc import ABC, abstractmethod

import pandas as pd

from solidago.poll import Poll
from solidago.poll.users import Users
from solidago.poll.vouches import Vouches

class TrustPropagation(ABC):
    """
    Base class for Trust Propagation algorithms
    """

    @staticmethod
    def init_state(users: pd.DataFrame, vouches: pd.DataFrame):
        """
        Temporary helper to use implementations from solidago.poll_functions
        until the pipeline is fully migrated to Poll + PollFunction.
        """
        state_users = Users.from_dict({
            (user.Index,): ("", user.is_pretrusted, 0.0)
            for user in users.itertuples()
        })
        state_vouches = Vouches.from_dict({
            (vouch.voucher, vouch.vouchee, "Personhood"): (vouch.vouch, 0.0)
            for vouch in vouches.itertuples()
        })
        return Poll.empty().assign(users=state_users, vouches=state_vouches)

    @abstractmethod
    def __call__(self,
        users: pd.DataFrame,
        vouches: pd.DataFrame
    ) -> pd.DataFrame:
        """ Propagates trust through vouch network
        
        Parameters
        ----------
        users: DataFrame
            with columns

            * user_id (int, index)
            * is_pretrusted (bool)

        vouches: DataFrame
            with columns

            * voucher (str)
            * vouchee (str)
            * vouch (float)
        
        Returns
        -------
        users: DataFrame
            with columns

            * user_id (int, index)
            * is_pretrusted (bool)
            * trust_score (float)
        """
        raise NotImplementedError
        
    def __str__(self):
        return type(self).__name__
		
    def to_json(self):
        return (type(self).__name__, )
