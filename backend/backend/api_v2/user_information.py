from backend.api_v2.helpers import Base64ImageField, WithNestedWritableFields, MarkerField
from backend.api_v2.helpers import WithUpdatedDocstringsDecorator, WithPKOverflowProtection
from backend.models import UserInformation, EmailDomain
from backend.models import VerifiableEmail, Degree, Expertise, ExpertiseKeyword
from backend.user_verify import send_verification_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_react.get_username import current_user
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class ExpertiseSerializer(serializers.ModelSerializer):
    """Expertise"""

    class Meta:
        model = Expertise
        fields = ('name',)


class ExpertiseKeywordSerializer(serializers.ModelSerializer):
    """Expertise keyword"""

    class Meta:
        model = ExpertiseKeyword
        fields = ('name',)


class DegreeSerializer(serializers.ModelSerializer):
    """Degree"""

    class Meta:
        model = Degree
        fields = ('level', 'domain', 'institution')


class VerifiableEmailSerializer(serializers.ModelSerializer):
    """E-mail"""

    class Meta:
        model = VerifiableEmail
        fields = ('email', 'is_verified')
        read_only_fields = ['is_verified']


class OnlyUsernameSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize user information, give only username."""

    class Meta:
        model = UserInformation
        fields = ['username']
        read_only_fields = ['username']


class UserInformationPublicSerializerV2(
        WithNestedWritableFields,
        serializers.HyperlinkedModelSerializer):
    """User Profile"""

    username = serializers.CharField(help_text="Username", read_only=True)
    avatar = Base64ImageField(
        help_text="Profile picture",
        use_url=True,
        required=False)
    degrees = DegreeSerializer(many=True, help_text="Degrees", required=False)
    expertises = ExpertiseSerializer(
        many=True, help_text="Expertises", required=False)
    expertise_keywords = ExpertiseKeywordSerializer(
        many=True, help_text="Expertise keywords", required=False)
    emails = VerifiableEmailSerializer(
        many=True, help_text="E-mails", required=False)
    n_ratings = serializers.IntegerField(
        help_text="Number of ratings", read_only=True)
    n_videos = serializers.IntegerField(
        help_text="Number of rated videos", read_only=True)
    n_comments = serializers.IntegerField(
        help_text="Number of comments left", read_only=True)
    n_likes = serializers.IntegerField(
        help_text="Number of likes minus number of dislikes for comments",
        read_only=True)
    is_certified = serializers.BooleanField(
        help_text="E-mail domain is certified", read_only=True)
    is_domain_rejected = serializers.BooleanField(
        help_text="Any e-mail domain is rejected", read_only=True)
    comment_anonymously = serializers.BooleanField(
        help_text="By default, comment anonymously")
    n_mentions = serializers.IntegerField(help_text="Number of mentions in comments",
                                          read_only=True)

    n_thanks_given = serializers.IntegerField(
        help_text="Number of thank you for recommendations given", read_only=True)
    n_thanks_received = serializers.IntegerField(
        help_text="Number of thank you for recommendations received", read_only=True)
    n_public_videos = serializers.IntegerField(
        help_text="Number of videos rated publicly", read_only=True)

    # markers to separate parts of the form, only visible in schema
    title_userprofile = MarkerField()
    title_email = MarkerField()
    title_degree = MarkerField()
    title_expertise_keywords = MarkerField()
    title_expertise = MarkerField()
    title_demographic = MarkerField()
    title_online = MarkerField()

    certified_email_domain = serializers.SerializerMethodField(
        help_text="Certified e-mail domain, starting with @",
        read_only=True, allow_null=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_certified_email_domain(self, user):
        """Get accepted email domain with a verified e-mail, or None."""
        qs = VerifiableEmail.objects.filter(user=user, is_verified=True,
                                            domain_fk__status=EmailDomain.STATUS_ACCEPTED)
        if qs:
            item = qs.first()
            return item.domain
        else:
            return None

    def to_representation(self, obj):
        """Removing data dynamically to protect privacy #27."""
        ret = super(
            UserInformationPublicSerializerV2,
            self).to_representation(obj)
        if current_user().username != obj.user.username:
            for field in self.Meta.delete_for_others:
                ret.pop(field)

            if not obj.show_online_presence:
                for field in self.Meta.online_presence:
                    ret.pop(field)

        # remove help fields in output
        for field in list(ret.keys()):
            if isinstance(self.fields[field], MarkerField):
                ret.pop(field)

        # not allowing None avatar field
        if 'avatar' in ret and ret['avatar'] is None:
            del ret['avatar']

        return ret

    class Meta:
        model = UserInformation

        # the fields order defines the form as well
        fields = [
            # USER PROFILE SECTION
            'title_userprofile',
            'show_my_profile',
            'avatar', 'first_name', 'last_name', 'comment_anonymously', 'title', 'bio',
            'id', 'username', 'n_ratings', 'n_videos', 'n_comments', 'n_likes',
            'n_thanks_given', 'n_thanks_received', 'n_mentions',
            'n_public_videos',

            # E-mails
            'title_email',
            'emails', 'is_certified', 'is_domain_rejected',
            'certified_email_domain',

            # Degrees
            'title_degree',
            'degrees',

            # Expertises
            'title_expertise',
            'expertises',

            # Expertise keywords
            'title_expertise_keywords',
            'expertise_keywords',

            # Demographic data
            'title_demographic',
            'gender', 'birth_year', 'nationality', 'residence',
            'race', 'political_affiliation',
            'degree_of_political_engagement',
            'religion', 'moral_philosophy',

            # Online Presence
            'title_online',
            'show_online_presence', 'google_scholar', 'website', 'linkedin', 'orcid', 'twitter',
            'researchgate',
            'youtube'
        ]
        nested_fields = {'expertises': ExpertiseSerializer,
                         'expertise_keywords': ExpertiseKeywordSerializer,
                         'degrees': DegreeSerializer,
                         'emails': VerifiableEmailSerializer}
        nested_preprocess = {
            'emails': lambda x: {
                'email': x.get(
                    'email', None)}}

        # remove these fields for users who are not me
        delete_for_others = [
            'emails',
            'birth_year',
            'gender',
            'nationality',
            'race',
            'political_affiliation',
            'religion',
            'degree_of_political_engagement',
            'residence',
            'moral_philosophy']

        # remove these fields if online presense is not allowed
        online_presence = [
            'orcid',
            'twitter',
            'website',
            'linkedin',
            'youtube',
            'google_scholar',
            'researchgate']


def accessible_model_filter(queryset, username):
    """List of accessible for search models."""
    queryset = UserInformation._annotate_n_public_videos(queryset)
    queryset = queryset.filter(
        (Q(is_demo=False) & Q(_n_public_videos__gte=1)) |
        Q(user__username=username))
    return queryset


class UserInformationFilterV2(filters.FilterSet):
    """Filter user informations."""

    class Meta:
        model = UserInformation
        fields = ['user__username']


class IsMineOrReadOnly(permissions.BasePermission):
    """Read-only or user.username == request.user.username. """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user.username == request.user.username


@WithUpdatedDocstringsDecorator
class UserInformationViewSetV2(mixins.ListModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.RetrieveModelMixin,
                               WithPKOverflowProtection,
                               viewsets.GenericViewSet, ):
    """Get and set my UserInformation."""

    filterset_class = UserInformationFilterV2
    permission_classes = [IsMineOrReadOnly]

    UPDATE_DOCSTRING = {
        'list': "List and filter user information",
        'retrieve': "Get information about one user",
        'update': "Replace my user information",
        'partial_update': "Partially update my user information"}

    KWARGS_DICT = {
        'update': {
            'responses': {
                403: None,
                400: None,
                404: None,
                201: UserInformationPublicSerializerV2,
                200: UserInformationPublicSerializerV2}},
        'partial_update': {
            'responses': {
                403: None,
                400: None,
                404: None,
                201: UserInformationPublicSerializerV2,
                200: UserInformationPublicSerializerV2}},
        'retrieve': {
            'responses': {
                404: None,
                200: UserInformationPublicSerializerV2}},
        'list': {
            'responses': {
                200: UserInformationPublicSerializerV2(
                    many=True),
                400: None}}}

    queryset = UserInformation.objects.all()
    serializer_class = UserInformationPublicSerializerV2

    def get_queryset(self):
        """Filter people who don't want to be shown."""
        qs = self.queryset.filter(Q(show_my_profile=True) | Q(
            user__username=self.request.user.username))
        return qs

    @extend_schema(
        responses={
            201: VerifiableEmailSerializer(
                many=False),
            400: None,
            404: None,
            403: None},
        parameters=[
            OpenApiParameter(
                name='email',
                description='E-mail to verify',
                required=True,
                type=str),
        ],
        request=inline_serializer(
            name="Empty",
            fields={}))
    @action(methods=['PATCH'], detail=True)
    def verify_email(self, request, pk=None):
        """Ask for e-mail verification."""
        obj = self.get_object()

        email_str = request.data.get('email', '')
        email = get_object_or_404(VerifiableEmail, email=email_str, user=obj)

        if email.is_verified:
            return Response(
                status=400, data={
                    'detail': "E-mail is verified already"})

        send_verification_email(email)
        s = VerifiableEmailSerializer(email, many=False)
        return Response(dict(s.data), status=201)

    @extend_schema(
        responses={
            201: VerifiableEmailSerializer(
                many=True),
            400: None,
            404: None,
            403: None},
        parameters=[],
        request=inline_serializer(
            name="Empty",
            fields={}))
    @action(methods=['PATCH'], detail=True)
    def verify_all_emails(self, request, pk=None):
        """Ask for e-mail verification for all unverified e-mails."""
        obj = self.get_object()

        # unverified e-mails
        qs = VerifiableEmail.objects.filter(user=obj, is_verified=False)

        # sending confirmation
        for email in qs:
            send_verification_email(email)

        # returning data
        s = VerifiableEmailSerializer(qs, many=True)
        return Response({'results': list(s.data), 'count': len(
            s.data), 'previous': None, 'next': None}, status=201)

    @extend_schema(
        responses={
            201: VerifiableEmailSerializer(
                many=False),
            400: None,
            404: None,
            403: None},
        parameters=[
            OpenApiParameter(
                name='email',
                description='E-mail to add and ask to verify',
                required=True,
                type=str),
        ],
        request=inline_serializer(
            name="Empty",
            fields={}))
    @action(methods=['PATCH'], detail=True)
    def add_verify_email(self, request, pk=None):
        """Add an address and ask for verification."""
        obj = self.get_object()

        email = request.query_params.get('email', None)

        try:
            email, created = VerifiableEmail.objects.get_or_create(
                user=obj, email=email)
        except IntegrityError as e:
            raise serializers.ValidationError(e)
        except Exception as e:
            raise e

        send_verification_email(email)

        # returning data
        s = VerifiableEmailSerializer(email, many=False)
        return Response(s.data, status=201)

    @extend_schema(responses={200: OnlyUsernameSerializer(many=True),
                              400: None},
                   parameters=[],
                   request=inline_serializer(name="Empty", fields={}))
    @action(methods=['GET'], detail=False)
    def public_models(self, request, pk=None):
        """Ask for e-mail verification for all unverified e-mails."""
        queryset = UserInformation.objects.all()
        queryset = accessible_model_filter(
            queryset, username=self.request.user.username)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OnlyUsernameSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OnlyUsernameSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses={200: OnlyUsernameSerializer(many=True),
                              400: None},
                   parameters=[OpenApiParameter(name="search_query",
                                                type=str,
                                                required=True,
                                                description="Search for this"
                                                            " string in user names")])
    @action(methods=['GET'], detail=False)
    def search_username(self, request):
        search_query = request.query_params.get('search_query', '')
        try:
            limit = int(request.query_params.get('limit', 20))
            assert limit >= 0, "Limit must be positive"
        except Exception as e:
            return Response({'reason': str(e)}, status=400)

        qs = UserInformation.objects.all()
        qs = UserInformation._annotate_is_certified(qs)
        qs = qs.filter(_is_certified=True)
        qs = qs.filter(user__username__icontains=search_query)
        qs = qs.order_by('user__username')
        qs = qs[:limit]
        serializer = OnlyUsernameSerializer(qs, many=True)
        return Response({'results': serializer.data,
                         'count': len(qs),
                         'previous': None,
                         'next': None})

    @extend_schema(responses={200: ExpertiseSerializer(many=True),
                              400: None},
                   parameters=[OpenApiParameter(name="search_query",
                                                type=str,
                                                required=True,
                                                description="Search for this"
                                                            " string in expertises")])
    @action(methods=['GET'], detail=False)
    def search_expertise(self, request, limit=20):
        search_query = request.query_params.get('search_query', '')
        qs = Expertise.objects.all()
        qs1 = ExpertiseKeyword.objects.all()
        qs = qs.filter(name__icontains=search_query).values('name').distinct()
        qs1 = qs1.filter(name__icontains=search_query).values('name').distinct()

        qs = list(qs[:limit]) + list(qs1[:limit])
        qs = [x['name'] for x in qs]
        qs = list(set(qs))[:limit]
        qs = sorted(qs)
        qs = [{'name': x} for x in qs]
        serializer = ExpertiseSerializer(qs, many=True)
        return Response({'results': serializer.data,
                         'count': len(qs),
                         'previous': None,
                         'next': None})

    def perform_update(self, serializer):
        # setting the user automatically
        with transaction.atomic():
            try:
                serializer.save()
            except ValidationError as e:
                raise serializers.ValidationError(e.message_dict)
            except Exception as e:
                raise e
