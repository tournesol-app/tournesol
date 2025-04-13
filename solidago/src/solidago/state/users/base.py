from typing import Union
from solidago.primitives.datastructure.objects import Object, Objects


class User(Object):
    def __init__(self, name: Union[str, int], vector: list=[], trust: float=1., **kwargs):
        super().__init__(name, vector, **kwargs)
        try:
            self.trust = float(trust)
        except ValueError:
            self.trust = 0.0


class Users(Objects):
    name: str="users"
    index_name: str="username"
    object_cls: type=User
    
    def __init__(self, init_data=None):
        super().__init__(init_data)

