from solidago.state.wrappers.named_dataframe import NamedSeries, NamedDataFrame


class User(NamedSeries):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Users(NamedDataFrame):
    index_name = "username"
    series_class = User
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, save_filename="users.csv", **kwargs)
