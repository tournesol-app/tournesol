"""
The `faq` app routes.
We keep this file to ensure retro-compatibility with clients still using
/faq/ endpoint instead of /backoffice/faq/
"""

from django.urls import path

from backoffice.views import FAQEntryLocalizedListView

urlpatterns = [
    path(
        "faq/",
        FAQEntryLocalizedListView.as_view(),
        name="faq_list_localized",  # pylint: disable=duplicate-code
    ),
]
