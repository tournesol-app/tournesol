from solidago.state import Users, Vouches


class VouchGenerator:
    
    def __call__(self, users: Users) -> Vouches:
        return Vouches()
    
    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )

