from typing import Optional

class VotingRights:
    def __init__(self, dct: Optional[dict[int, dict[int, float]]]=None):
        """ Initialize voting rights
        
        Parameters
        ----------
        dct: dict[int, dict[int, float]]
            dct[entity][user] is the voting right of user for entity
        """
        self._dict = dict() if dct is None else dct
    
    def __getitem__(self, user_entity_tuple:tuple[int, int]) -> float:
        """ self[user, entity] must returns the voting right of a user for an entity
                
        Parameters
        ----------
        user_entity_tuple: (user: int, entity: int)
        
        Returns
        -------
        out: float
        """
        user, entity = user_entity_tuple
        if entity not in self._dict:
            return 0
        if user not in self._dict[entity]:
            return 0
        return self._dict[entity][user]
    
    def __setitem__(self, user_entity_tuple:tuple[int, int], value: float):
        """ sets the voting right of a user for an entity
                
        Parameters
        ----------
        user_entity_tuple: (user: int, entity: int)
        value: float
        """
        user, entity = user_entity_tuple
        if entity not in self._dict:
            self._dict[entity] = dict()
        self._dict[entity][user] = value

    def entities(self, user: Optional[int] = None) -> set[int]:
        if user is None:
            return set(self._dict.keys())
        return { e for e in self._dict if user in self._dict[e] }
        
    def on_entity(self, entity: int) -> dict[int, float]:
        return self._dict[entity]

