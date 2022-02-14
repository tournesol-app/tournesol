from abc import ABC, abstractclassmethod


class EntityType(ABC):
    name: str

    @classmethod
    def filter_date_lte(cls, qs, dt):
        return qs.filter(add_time__lte=dt)

    @classmethod
    def filter_date_gte(cls, qs, dt):
        return qs.filter(add_time__gte=dt)

    @abstractclassmethod
    def filter_search(cls, qs, query: str):
        raise NotImplementedError
