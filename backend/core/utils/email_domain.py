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


def count_accounts_by_domains_on_day(
    day: datetime.date, status: str = EmailDomain.STATUS_ACCEPTED, min_n_account: int = 1
) -> RawQuerySet:
    """
    Return all email domains with the number of related user accounts created on
    the given date.
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

        WHERE date_trunc('day', u.date_joined) = %(day)s
          AND e.status = %(status)s

        GROUP BY e.domain, e.id
        HAVING count(*) >= %(min_n_account)s
        ORDER BY cnt DESC;
        """,
        {
            "day": day.strftime("%Y-%m-%d"),
            "status": status,
            "min_n_account": min_n_account,
        },
    )


def count_accounts_by_filtered_domains_until(
    pks: list[int], until: datetime.datetime, min_n_account: int = 1
) -> RawQuerySet:
    """
    Given a list of EmailDomain pk, return the number of related user accounts
    created before the given date.
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

        WHERE e.id = ANY(%(pks)s)
          AND u.date_joined <= %(until)s

        GROUP BY e.domain, e.id
        HAVING count(*) >= %(min_n_account)s
        ORDER BY cnt DESC;
        """,
        {
            "pks": pks,
            "until": until.strftime("%Y-%m-%d %H:%M:%S"),
            "min_n_account": min_n_account,
        },
    )
