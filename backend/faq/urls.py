"""
The `faq` app routes.
"""

from django.urls import path

from faq.views import FAQEntryLocalizedListView

urlpatterns = [
    path(
        "faq/",
        FAQEntryLocalizedListView.as_view(),
        name="faq_list_localized",
    ),
]
