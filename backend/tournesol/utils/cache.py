from django.conf import settings
from django.utils import translation
from django.views.decorators.cache import cache_page


def cache_page_no_i18n(timeout: float):
    """
    This decorator activates the default language before calling the Django's
    decorator `cache_page`.

    By default, `cache_page` includes the request language code in its cache
    key. Some API responses (e.g. public export files) don't depend on the
    language and can be cached under a single key using this decorator.

    Keyword arguments:
    timeout -- time to live of the cached page, in seconds.
    """

    def decorator(view):
        cached_view = cache_page(timeout=timeout)(view)

        def wrapper(request, *args, **kwargs):
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = translation.get_language()
            return cached_view(request, *args, **kwargs)

        return wrapper

    return decorator
