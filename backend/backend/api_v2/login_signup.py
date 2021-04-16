from backend.api_v2.helpers import WithUpdatedDocstringsDecorator, WithPKOverflowProtection
from backend.models import DjangoUser
from backend.models import UserInformation
from backend.models import VerifiableEmail
from backend.reset_password import reset_password
from backend.user_verify import send_verification_email
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django_react import settings
from django_react.get_username import current_user
from drf_recaptcha.fields import ReCaptchaV2Field
from drf_spectacular.utils import extend_schema
from frontend.views import create_user_preferences
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator


class LoginSerializer(serializers.ModelSerializer):
    """Log in a user with username and a password"""
    username = serializers.CharField(required=True, help_text="Your username")

    password = serializers.CharField(write_only=True, required=True, help_text="Your password")

    class Meta:
        model = DjangoUser
        fields = ('username', 'password')

    def update(self, validated_data):
        pass


class ResetPasswordSerializer(serializers.ModelSerializer):
    """Reset a password"""
    username = serializers.CharField(required=True, help_text="Your username")

    recaptcha = ReCaptchaV2Field(required=not settings.NOCAPTCHA)

    class Meta:
        model = DjangoUser
        fields = ('username', 'recaptcha')


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Change password"""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password],
                                     help_text="Your new password")
    password2 = serializers.CharField(write_only=True, required=True,
                                      help_text="Repeat your new password again")

    class Meta:
        model = DjangoUser
        fields = ('password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = DjangoUser.objects.get(username=self.context['request'].user.username)
        user.set_password(validated_data['password'])
        user.save()

        return user


class RegisterSerializer(serializers.ModelSerializer):
    """Register a user"""
    username = serializers.CharField(required=True, help_text="Your new username",
                                     validators=[
                                         UniqueValidator(queryset=DjangoUser.objects.all())], )

    email = serializers.EmailField(
        required=True,
        help_text="Your e-mail address"
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password],
                                     help_text="Your new password")
    password2 = serializers.CharField(write_only=True, required=True,
                                      help_text="Repeat your new password again")

    # name changed for the field to work with https://github.com/benchesh/Cookie-Notice-Blocker
    shrivacy_policy = serializers.BooleanField(write_only=True,
                                               required=False,
                                               help_text="I have read and I accept"
                                                         " the privacy policy")
    recaptcha = ReCaptchaV2Field(required=not settings.NOCAPTCHA)

    class Meta:
        model = DjangoUser
        fields = ('username', 'password', 'password2', 'email', 'recaptcha', 'shrivacy_policy')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        if not attrs.get('shrivacy_policy', False):
            raise serializers.ValidationError({'shrivacy_policy': "Please accept the privacy policy"
                                                                  " to sign up for Tournesol"})
        return attrs

    def create(self, validated_data):
        user = None
        try:
            user = DjangoUser.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                is_active=False,
            )

            user_info = UserInformation.objects.create(user=user)
            email = VerifiableEmail.objects.create(
                email=user.email, user=user_info, is_verified=False)

            # creating preferences for a new user
            # return redirect(f'/email_show_instructions/{user.email}')
        except Exception as e:
            raise serializers.ValidationError({'username': [str(e)]})

        create_user_preferences()
        send_verification_email(email)

        return user


class OnlyUsernameAndIDSerializer(serializers.HyperlinkedModelSerializer):
    """Change login name"""

    username = serializers.CharField(read_only=False, source='user.username',
                                     help_text="New login name")

    class Meta:
        model = UserInformation
        fields = ['id', 'username']

    def update(self, instance, validated_data):
        if not instance.user:
            return instance
        if validated_data.get('user', {}).get('username', None) is None:
            return instance
        instance.user.username = validated_data['user']['username']
        instance.user.save()
        logout(self.context['request'])
        return instance


class IsMine(permissions.BasePermission):
    """Only allow access to my information."""

    def has_object_permission(self, request, view, obj):
        return obj.user.username == request.user.username


@WithUpdatedDocstringsDecorator
class LoginSignupViewSetV2(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           WithPKOverflowProtection,
                           viewsets.GenericViewSet, ):
    """Log in, log out, sign up, reset password, change password, authenticate."""

    permission_classes = [IsMine]

    def get_queryset(self):
        return UserInformation.objects.filter(user__username=current_user().username)

    UPDATE_DOCSTRING = {
        'list': "Get my username in a list",
        'retrieve': "Get my username by my user preferences id",
        'update': "Update my username",
        'partial_update': "Update my username"}

    KWARGS_DICT = {
        'update': {
            'responses': {
                403: None,
                400: None,
                404: None,
                201: OnlyUsernameAndIDSerializer,
                200: OnlyUsernameAndIDSerializer}},
        'partial_update': {
            'responses': {
                403: None,
                400: None,
                404: None,
                201: OnlyUsernameAndIDSerializer,
                200: OnlyUsernameAndIDSerializer}},
        'retrieve': {
            'responses': {
                404: None,
                200: OnlyUsernameAndIDSerializer}},
        'list': {
            'responses': {
                200: OnlyUsernameAndIDSerializer(
                    many=True),
                400: None}}}

    serializer_class = OnlyUsernameAndIDSerializer

    def perform_update(self, serializer, method='save'):
        # setting the user automatically
        with transaction.atomic():
            try:
                m = getattr(serializer, method)
                return m()
            except ValidationError as e:
                raise serializers.ValidationError(e.message_dict)
            except IntegrityError as e:
                raise serializers.ValidationError({'username': [str(e)]})
            except Exception as e:
                raise e

    @extend_schema(responses={200: OnlyUsernameAndIDSerializer,
                              400: None},
                   request=RegisterSerializer)
    @action(methods=['POST'], detail=False, name="Register a user")
    def register(self, request):
        """Register a user."""
        print(request.data)
        s_obj = RegisterSerializer(data=request.data, context={"request": request})
        if s_obj.is_valid(raise_exception=True):
            data = s_obj.validated_data
            print(data)
        user = self.perform_update(s_obj)

        s_ret = OnlyUsernameAndIDSerializer(DjangoUser.objects.get(
            username=user.username))
        return Response(s_ret.data, status=200)

    @extend_schema(responses={200: OnlyUsernameAndIDSerializer,
                              400: None},
                   request=LoginSerializer)
    @action(methods=['PATCH'], detail=False, name="Log in with username/password")
    def login(self, request):
        """Register a user."""
        username, password = request.data.get('username', ''), request.data.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                s_ret = OnlyUsernameAndIDSerializer(DjangoUser.objects.get(
                    username=user.username))

                return Response(s_ret.data, status=200)

        return Response({'detail': "Username is invalid or the password is invalid"},
                        status=400)

    @extend_schema(responses={200: None},
                   request=None)
    @action(methods=['PATCH'], detail=False, name="Log out")
    def logout(self, request):
        """Log out."""
        logout(request)
        return Response(status=200)

    @extend_schema(responses={200: None,
                              400: None},
                   request=ResetPasswordSerializer)
    @action(methods=['PATCH'], detail=False, name="Reset password")
    def reset_password(self, request):
        """Reset password."""
        s_obj = ResetPasswordSerializer(data=request.data, context={"request": request})
        if s_obj.is_valid(raise_exception=True):
            data = s_obj.validated_data
            try:
                reset_password(data['username'])
            except Exception as e:
                print(e)
                pass

        return Response(status=200)

    @extend_schema(responses={200: OnlyUsernameAndIDSerializer,
                              400: None},
                   request=ChangePasswordSerializer)
    @action(methods=['PATCH'], detail=False, name="Change password")
    def change_password(self, request):
        """Change password"""
        s_obj = ChangePasswordSerializer(data=request.data, context={"request": request})
        if s_obj.is_valid(raise_exception=True):
            user = self.perform_update(s_obj)

            s_ret = OnlyUsernameAndIDSerializer(DjangoUser.objects.get(
                username=user.username))
        return Response(s_ret.data, status=200)
