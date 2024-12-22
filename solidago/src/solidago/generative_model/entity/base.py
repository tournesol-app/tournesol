import pandas as pd

from solidago.state import Entities


class EntityGenerator:
    def __call__(self, n_entities: int) -> Entities:
        df = pd.DataFrame([ self.entity_generate() for _ in range(n_entities) ])
        df.index.name = "entity_id"
        return Entities(df)
    
    def user_generate(self):
        return pd.Series()
        
    def __str__(self):
        return type(self).__name__
    
    def to_json(self):
        return (type(self).__name__, )


