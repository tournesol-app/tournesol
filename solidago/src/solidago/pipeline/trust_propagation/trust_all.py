from .base import TrustPropagation
from solidago.state import Users, Vouches


class TrustAll(TrustPropagation):
    """`TrustAll` is a naive solution that assignes an equal amount of trust to all users"""
    def main(self, users: Users, vouches: Vouches) -> Users:
        users["trust_score"] = 1.
        return users
