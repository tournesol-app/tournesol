"""
Defines additional validators for Tournesol's authentication
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    def get_additional_claims(self, request):
        return {
            "sub": request.user.username,
            "username": request.user.username,
            "preferred_username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "role": "admin" if request.user.is_superuser else "user",
        }

    def get_userinfo_claims(self, request):
        claims = super().get_userinfo_claims(request)
        return claims

    def validate_user(self, username, password, client, request, *args, **kwargs):
        user_found = super().validate_user(username, password, client, request, *args, **kwargs)
        if user_found:
            return user_found
        # support authentication with email as username
        if not user_found and username and "@" in username:
            try:
                user = get_user_model().objects.get(email=username)
            except ObjectDoesNotExist:
                return False
            return super().validate_user(user.username, password, client, request, *args, **kwargs)

    def save_bearer_token(self, token, request, *args, **kwargs):
        if request.user.is_authenticated:
            token["username"] = request.user.username
        return super().save_bearer_token(token, request, *args, **kwargs)
