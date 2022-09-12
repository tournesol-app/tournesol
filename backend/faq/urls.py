"""
The `faq` app routes.
"""

from django.urls import path

from faq.views import FAQuestionLocalizedListView

urlpatterns = [
    path(
        "faq/",
        FAQuestionLocalizedListView.as_view(),
        name="faq_list_localized",
    ),
]
