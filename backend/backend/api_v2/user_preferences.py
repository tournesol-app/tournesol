from backend.api_v2.helpers import WithUpdatedDocstringsDecorator, WithPKOverflowProtection
from backend.models import UserPreferences, DjangoUser
from backend.rating_fields import VIDEO_FIELDS
from rest_framework import mixins
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class UserPreferencesSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize UserPreferences."""

    username = serializers.CharField(
        help_text="Username for this user preferences' user",
        read_only=True)

    class Meta:
        model = UserPreferences
        fields = ['id'] + VIDEO_FIELDS + ['username'] +\
                 [x + '_enabled' for x in VIDEO_FIELDS] +\
                 ['rating_mode']
        read_only_fields = ['id', 'username']


@WithUpdatedDocstringsDecorator
class UserPreferencesViewSetV2(mixins.UpdateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               WithPKOverflowProtection,
                               viewsets.GenericViewSet, ):
    """Get and set my User Preferences."""

    UPDATE_DOCSTRING = {
        'list': "Show my user preferences in a list",
        'retrieve': "Get user preferences",
        'update': "Change all fields in user preferences",
        'partial_update': "Change some fields in user preferences"}

    KWARGS_DICT = {
        'retrieve': {
            'responses': {
                404: None, 200: UserPreferencesSerializerV2}}, 'update': {
            'responses': {
                404: None, 200: UserPreferencesSerializerV2}}, 'partial_update': {
            'responses': {
                404: None, 200: UserPreferencesSerializerV2}}, 'list': {
            'responses': {
                404: None, 400: None, 200: UserPreferencesSerializerV2(many=True),
            }}}

    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializerV2

    def get_queryset(self, pk=None):
        """Only allow accessing own user preferences."""
        django_user = DjangoUser.objects.get(
            username=self.request.user.username)
        return UserPreferences.objects.filter(user=django_user)

    @action(methods=['GET', 'PATCH'], detail=False,
            name="Get/Set my own user preferences.")
    def my(self, request):
        """Get/set my own user preferences."""
        user_preferences = self.get_queryset().get()
        if request.method == 'GET':
            return Response(self.get_serializer(user_preferences).data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user_preferences, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
