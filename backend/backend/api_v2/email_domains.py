from backend.api_v2.helpers import WithUpdatedDocstringsDecorator, WithPKOverflowProtection
from backend.models import EmailDomain
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q, Count


class EmailDomainSerializer(serializers.ModelSerializer):
    """E-mail domain"""

    n_verified_emails = serializers.IntegerField(
            read_only=True, help_text="Number of verified emails with ths domain")

    class Meta:
        model = EmailDomain
        fields = ('domain', 'status', 'n_verified_emails')


class EmailDomainFilterV2(filters.FilterSet):
    """Filter domains."""

    class Meta:
        model = EmailDomain
        fields = ['status']


@WithUpdatedDocstringsDecorator
class EmailDomainViewSetV2(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           WithPKOverflowProtection,
                           viewsets.GenericViewSet, ):
    """List of Email Domains"""

    filterset_class = EmailDomainFilterV2
    permission_classes = [IsAuthenticatedOrReadOnly]

    UPDATE_DOCSTRING = {'list': "List e-mail domains",
                        'retrieve': "Get e-mail domain"}

    KWARGS_DICT = {
        'retrieve': {
            'responses': {
                404: None, 200: EmailDomainSerializer}}, 'list': {
            'responses': {
                200: EmailDomainSerializer(
                    many=True), 400: None}}}

    queryset = EmailDomain.objects.all().filter(status=EmailDomain.STATUS_ACCEPTED).\
        annotate(n_verified_emails=Count('verifiable_emails_domain',
                                         filter=Q(verifiable_emails_domain__is_verified=True))).\
        order_by('-n_verified_emails')
    serializer_class = EmailDomainSerializer
