from rest_framework import generics, pagination

from core.models import EmailDomain
from core.serializers.email_domain import EmailDomainSerializer


class EmailDomainPagination(pagination.LimitOffsetPagination):
    default_limit = 1000


class EmailDomainsList(generics.ListAPIView):
    """
    List all accepted (=trusted) email domains.
    """

    queryset = EmailDomain.objects.filter(status=EmailDomain.STATUS_ACCEPTED).order_by(
        "domain"
    )
    pagination_class = EmailDomainPagination
    serializer_class = EmailDomainSerializer
    permission_classes = []
