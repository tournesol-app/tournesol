import solidago


class Assessment(solidago.Assessment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
class Assessments(solidago.Assessments):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
