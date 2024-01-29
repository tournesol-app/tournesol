from .base import Scaling


class ScalingCompose(Scaling):
    """ Class used to compose any number of scaling solutions """    
    def __init__(self, *scalings: Scaling):
        """ Composes a list of scalings
        """
        self.scalings = scalings
        
    def __call__(self, user_models, users, entities, voting_rights, privacy):
        scaled_models = user_models
        for scaling in self.scalings:
            scaled_models = scaling(scaled_models, users, entities, voting_rights, privacy)
        return scaled_models

    def to_json(self):
        scalings_json = [scaling.to_json() for scaling in self.scalings]
        return type(self).__name__, scalings_json
