from typing import Union
from solidago.primitives.datastructure.objects import Object, Objects


class Entity(Object):
    def __init__(self, name: Union[str, int], trust: float=1, vector: list=[], **kwargs):
        super().__init__(name, vector, **kwargs)
        self.trust = trust


class Entities(Objects):
    name: str="entities"
    index_name: str="entity_name"
    object_cls: type=Entity
    
    def __init__(self, init_data=None):
        super().__init__(init_data)

