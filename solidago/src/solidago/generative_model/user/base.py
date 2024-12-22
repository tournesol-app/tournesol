import pandas as pd

from solidago.state import Users


class UserGenerator:
    def __call__(self, n_users: int):
        df = pd.DataFrame([ self.user_generate() for _ in range(n_users) ])
        df.index.name = "username"
        return Users(df)
    
    def user_generate(self):
        return pd.Series()
    
    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )

