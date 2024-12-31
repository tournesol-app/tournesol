from solidago.primitives.datastructure.named_dataframe import NamedSeries, NamedDataFrame


class Criterion(NamedSeries):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Criteria(NamedDataFrame):
    index_name = "criterion_name"
    series_cls = Criterion
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, save_filename="criteria.csv", **kwargs)
