import solidago


class Entity(solidago.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
class Entities(solidago.Entities):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
