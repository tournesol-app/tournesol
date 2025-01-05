from solidago.primitives.datastructure.named_dataframe import NamedSeries, NamedDataFrame


class Entity(NamedSeries):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Entities(NamedDataFrame):
    index_name = "entity_name"
    series_cls = Entity
    
    def __init__(self, save_filename="entities.csv", *args, **kwargs):
        super().__init__(*args, save_filename=save_filename, **kwargs)
