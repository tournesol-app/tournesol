from rest_framework.serializers import ModelSerializer

from ..models import EmailDomain


class EmailDomainSerializer(ModelSerializer):
    class Meta:
        model = EmailDomain
        fields = ("domain", "status")
