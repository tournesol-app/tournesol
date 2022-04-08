from rest_framework.throttling import (
    AnonRateThrottle,
    ScopedRateThrottle,
    SimpleRateThrottle,
    UserRateThrottle,
)


class BurstAnonRateThrottle(AnonRateThrottle):
    """
    Limit the rate of API calls that may be made by an anonymous user.

    Should be used to define a rate for a short period of time.
    """

    scope = "anon_burst"


class BurstUserRateThrottle(UserRateThrottle):
    """
    Limit the rate of API calls that may be made by an authenticated user.

    Should be used to define a rate for a short period of time.
    """

    scope = "user_burst"


class SustainedAnonRateThrottle(AnonRateThrottle):
    """
    Limit the rate of API calls that may be made by an anonymous user.

    Should be used in addition to `BurstAnonRateThrottle` to define a rate
    that can be sustained for a longer period.
    """

    scope = "anon_sustained"


class SustainedUserRateThrottle(UserRateThrottle):
    """
    Limit the rate of API calls that may be made by an authenticated user.

    Should be used in addition to `BurstUserRateThrottle` to define a rate
    that can be sustained for a longer period.
    """

    scope = "user_sustained"


class PostScopeRateThrottle(ScopedRateThrottle):
    """
    Limit the rate of only HTTP POST requests made by an authenticated or
    an anonymous user.

    All other HTTP methods are authorized, and passed to the next throttle
    in the chain.
    """

    def allow_request(self, request, view):
        if request.method != "POST":
            return True
        return super().allow_request(request, view)


class GlobalEmailScopeThrottle(SimpleRateThrottle):
    """
    A global rate limit for POST requests involving email sending like the
    account creations, password reset, etc.

    This limit is shared by all clients.
    """

    scope = "email"

    def get_cache_key(self, request, view):
        if request.method != "POST":
            return None
        return "email_throttle"
