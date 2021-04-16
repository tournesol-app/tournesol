from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def settings_value(name):
    """Get value from the settings file.

    Taken from https://stackoverflow.com/questions/433162/can-i-access-\
    constants-in-settings-py-from-templates-in-django.
    """
    return getattr(settings, name, "")
