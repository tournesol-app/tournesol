from abc import abstractmethod

from solidago.poll import *

class WeightsCompute:
    @abstractmethod
    def __call__(self, 
        poll: Poll, 
        username: str, 
        column_name: str = "weight", 
        cursor: str | None = None
    ) -> Entities:
        raise NotImplemented
