"""
The `faq` app allows to manage an ordered FAQ by creating questions and
answers. These questions and answers can be translated in several languages.

For now, the questions form a single group. In the future, questions could be
grouped to create different FAQ.
"""

from django.apps import AppConfig


class FaqConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "faq"
