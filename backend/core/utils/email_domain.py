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
    Return the email domain with the number of account created `since` date with atleast
    `n_account`.

    Keyword arguments:

    since -- date from which the count start
    status -- email domain status: "ACK": accepted, "PD": pending, "RJ": rejected (default "ACK")
    n_account -- minimum number of account to be consider (default 1)

    Ex:
        get_email_domain_with_recent_new_users(datetime.datetime(2022,3,4), 10)
        Return all the domain name with 10 or more users created since the 4th of March 2022
    """
    return EmailDomain.objects.raw(
        """
        SELECT
            e.id,
            e.domain,
            count(*) as cnt
        FROM core_emaildomain AS e
        INNER JOIN (SELECT *, regexp_replace("email", '(.*)(@.*$)', '\\2')
        AS user_domain FROM core_user) AS u
        ON e.domain=u.user_domain
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
