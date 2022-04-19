from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from core.models.user import User


def validate_email_localpart_noplus(email: str, username="") -> str:
    email_split = email.split("@")
    """Raise ValidationError when similar emails are found in the database.
    
    Keyword arguments:
    email -- An email that is going to be written in the database.
    username -- The logged user's username, used to exclude him/herself from
                the validation when updating its own email. Empty for
                anonymous users.
    
    Emails considered similar when:
        - they share the same non-case-sensitive domain ;
        - they share, in the local part, the same non case-sensitive string
          before the `+` symbol.

    Examples of emails considered similar:
        - bob@example.org
        - bob+@example.org
        - bob+tournesol@example.org
        - BOB+tournesol@example.org
        - bob+hello@example.org
        - BOB+HELLO@example.org
        - etc.
    """

    # if there is no `@`, do nothing
    if len(email_split) == 1:
        return email

    local_part = email_split[0]
    local_part_split = local_part.split("+")

    # if there is no `+` symbol, do nothing
    if len(local_part_split) == 1:
        return email

    if username:
        users = User.objects.filter(
            email__istartswith=f"{local_part_split[0]}+",
            email__iendswith=f"@{email_split[-1]}",
        ).exclude(username=username)
    else:
        users = User.objects.filter(
            email__istartswith=f"{local_part_split[0]}+",
            email__iendswith=f"@{email_split[-1]}",
        )

    if users.exists():
        raise ValidationError(_("A user with this email address already exists."))

    return email
