from typing import Optional

class PrivacySettings:
    def __init__(self, dct=None):
        self._dict = dict() if dct is None else dct
        
    def __getitem__(self, user_entity_tuple: tuple[int, int]) -> Optional[bool]:
        """ Returns the user's privacy setting for a given entity
        The result may be True (for private), False (for public) or None (if undefined).
        
        Parameters
        ----------
        user_entity_tuple: (user: int, entity: int)
        
        Returns
        -------
        True (private), False (public) or None (undefined)
        """
        user, entity = user_entity_tuple
        entity_settings = self._dict.get(entity)
        if entity_settings is None:
            return None
        return entity_settings.get(user)
    
    def __setitem__(self, user_entity_tuple: tuple[int, int], is_private: Optional[bool]):
        """ Returns the user's privacy setting for a given entity
        The result may be True (for private), False (for public) or None (if undefined).
        
        Parameters
        ----------
        user_entity_tuple: (user: int, entity: int)
        is_private: True (private), False (public) or None (undefined)
        """
        user, entity = user_entity_tuple
        if is_private is None:
            self._dict[entity].pop(user, None)
            return
        self._dict.setdefault(entity, {})[user] = is_private

    def entities(self, user: Optional[int] = None) -> set[int]:
        if user is None:
            return set(self._dict.keys())
        return { e for e in self._dict if user in self._dict[e] }

    def users(self, entity: Optional[int] = None) -> set[int]:
        if entity is None:
            return set().union(*(self.users(e) for e in self.entities()))
        return set(self._dict.get(entity, {}).keys())

    def __str__(self):
        return "{\n    " + ",\n    ".join([
            "user " + str(user) + ": {\n        " + ",\n        ".join([
                f"entity {entity}: {self[user, entity]}"
                for entity in self.entities(user)
            ]) + "\n    }"
            for user in self.users()
        ]) + "\n}"
        
