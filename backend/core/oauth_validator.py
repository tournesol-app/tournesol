"""
Additional validators for the Tournesol's authentication
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    """Manage user authentication"""
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
        user_found = super().validate_user(
            username, password, client, request, *args, **kwargs
        )

        # Support authentication with email used as username
        if not user_found and username and "@" in username:
            user_model = get_user_model()

            try:
                user = user_model.objects.get(email=username)
            except ObjectDoesNotExist:
                try:
                    user = user_model.objects.get(email__iexact=username)
                except ObjectDoesNotExist:
                    return False
                except user_model.MultipleObjectsReturned:
                    return False

            return super().validate_user(
                user.username, password, client, request, *args, **kwargs
            )

        return user_found

    def save_bearer_token(self, token, request, *args, **kwargs):
        # Add 'username' field in token response
        if request.user.is_authenticated:
            token["username"] = request.user.username
        return super().save_bearer_token(token, request, *args, **kwargs)
