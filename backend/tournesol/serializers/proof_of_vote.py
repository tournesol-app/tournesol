from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class ProofOfVoteSerializer(Serializer):
    poll_name = CharField()
    signature = CharField()
