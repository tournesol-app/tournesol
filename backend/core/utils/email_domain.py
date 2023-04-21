"""
Shortcut functions related to the email domain.
"""
import datetime

from django.db.models.query import RawQuerySet

from core.models.user import EmailDomain


def get_email_domain_with_recent_new_users(
    since: datetime.datetime, status: str = EmailDomain.STATUS_ACCEPTED, n_account: int = 1
) -> RawQuerySet:
    """
    Return the email domains with the number of accounts created `since` the
    given date, having at least `n_account`.

    Keyword arguments:

    since -- include only accounts created since this date (included)
    status -- email domain status (default "ACK"):
                "ACK": accepted
                "PD": pending
                "RJ": rejected
    n_account -- minimum number of account to be considered (default 1)

    Ex:

    Return all the domain name with 10 or more users created since the 4th of
    March 2022:

        get_email_domain_with_recent_new_users(datetime.datetime(2022, 3, 4), 10)

    """
    return EmailDomain.objects.raw(
        """
        SELECT
            e.id,
            e.domain,
            count(*) as cnt

        FROM core_emaildomain AS e

        JOIN (
            SELECT *, regexp_replace("email", '(.*)(@.*$)', '\\2') AS user_domain
            FROM core_user
        ) AS u ON e.domain=u.user_domain

        WHERE u.date_joined >= %(since)s
          AND e.status = %(status)s

        GROUP BY e.domain, e.id
        HAVING count(*) >= %(n_account)s
        ORDER BY cnt DESC;
        """,
        {
            "since": since.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "n_account": n_account,
        },
    )


def get_domain_n_accounts_until(
    pk: int, until: datetime.datetime, min_n_account: int = 1
) -> RawQuerySet:
    """
    For a given EmailDomain identified by its primary key, return the number
    of accounts created `until` the specified date, only if at least
    `n_account` are present.

    Keyword arguments:

    until -- include only accounts created until this date (included)
    min_n_account -- minimum number of account to be considered (default 1)
    """
    return EmailDomain.objects.raw(
        """
        SELECT
            e.id,
            e.domain,
            count(*) as cnt

        FROM core_emaildomain AS e

        JOIN (
            SELECT *, regexp_replace("email", '(.*)(@.*$)', '\\2') AS user_domain
            FROM core_user
        ) AS u ON e.domain=u.user_domain

        WHERE e.id = %(pk)s
          AND u.date_joined <= %(until)s

        GROUP BY e.domain, e.id
        HAVING count(*) >= %(min_n_account)s
        LIMIT 1;
        """,
        {
            "pk": pk,
            "until": until.strftime("%Y-%m-%d %H:%M:%S"),
            "min_n_account": min_n_account,
        },
    )
