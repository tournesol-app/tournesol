from typing import Union
from solidago.primitives.datastructure.objects import Object, Objects


class User(Object):
    def __init__(self, name: Union[str, int], trust: float=1, vector: list=[], **kwargs):
        super().__init__(name, vector, **kwargs)
        self.trust = trust


class Users(Objects):
    name: str="users"
    index_name: str="username"
    object_cls: type=User
    
    def __init__(self, init_data=None):
        super().__init__(init_data)

