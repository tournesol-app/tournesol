from django.conf import settings
from django.utils import translation
from django.views.decorators.cache import cache_control, cache_page


def cache_page_no_i18n(timeout: float, public: bool = False):
    """
    Activates the default language before calling Django's `cache_page` decorator.

    By default, `cache_page` includes the request's language code in its cache
    key. This decorator allows API responses that do not depend on language
    (e.g., public export files) to be cached under a single, language-independent key.

    Keyword arguments:
    timeout -- Time to live for the cached page, in seconds.
    public -- Whether the `Cache-Control: public` header should be set on the response.
              In Django 5.2.15+, setting this header explicitly is required to cache
              responses for requests with an 'Authorization' header, regardless of the user.
              In Tournesol, cached responses typically do not depend on the user,
              so `public=True` is often appropriate here.
    """

    def decorator(view):
        if public:
            view = cache_control(public=True)(view)
        cached_view = cache_page(timeout=timeout)(view)

        def wrapper(request, *args, **kwargs):
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = translation.get_language()
            return cached_view(request, *args, **kwargs)

        return wrapper

    return decorator
