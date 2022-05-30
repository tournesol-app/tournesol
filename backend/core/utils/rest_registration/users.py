"""
Functions overriding the default rest_registration.utils.users module.
"""

from typing import Any, Dict

from rest_registration.exceptions import UserNotFound
from rest_registration.utils.users import get_user_by_lookup_dict, get_user_login_field_names

from core.models.user import User

# Keys are lookup fields of the `User` model that will be replaced by their
# value.
RESET_PASSWORD_USER_LOOKUPS_OVERRIDE = {"email": "email__iexact"}


def find_user_by_send_reset_password_link_data(
    data: Dict[str, Any], **kwargs: Any
) -> User:
    """
    Custom override of the default Django REST Registration function.

    Contrary to the original `find_user_by_by_send_reset_password_link_data`,
    function, this one provides a mechanism to use any Django field lookups to
    retrieve the user.

    In our case, it allows us to retrieve users with a non-case-sensitive
    email.
    """
    login_field_names = get_user_login_field_names()
    finder_tests = [("login", login_field_names)]
    finder_tests.extend((f, [f]) for f in login_field_names)

    for field_name, db_field_names in finder_tests:
        value = data.get(field_name)

        if value is None:
            continue

        for db_fn in db_field_names:
            lookup_field = RESET_PASSWORD_USER_LOOKUPS_OVERRIDE.get(db_fn)
            if not lookup_field:
                lookup_field = db_fn

            user = get_user_by_lookup_dict(
                {lookup_field: value}, default=None, require_verified=False
            )
            if user is not None:
                return user

    raise UserNotFound()
