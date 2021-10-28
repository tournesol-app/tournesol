"""
Defines Admin interface for Tournesol's core app
"""

from typing import List, Tuple
from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User,
    UserPreference,
    Degree,
    Expertise,
    ExpertiseKeyword,
    EmailDomain,
    VerifiableEmail,
)


@admin.register(UserPreference)
class UserPreferencesAdmin(admin.ModelAdmin):
    pass


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ['-date_joined']

    def get_fieldsets(self, request, obj) -> List[Tuple]:
        fieldsets = super().get_fieldsets(request, obj=obj)
        if not obj:
            return fieldsets

        # For existing user, show all fields from our custom User model that
        # are not already present on the page, in a separate fieldsets.
        existing_fields = flatten_fieldsets(fieldsets)
        return fieldsets + (
            ('Other fields', {
                'classes': ('collapse',),
                'fields': tuple(
                    f.name
                    for f in User._meta.local_fields
                    if f.name != 'id' and f.name not in existing_fields
                ),
            }),
        )


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    pass


@admin.register(ExpertiseKeyword)
class ExpertiseKeywordAdmin(admin.ModelAdmin):
    pass


@admin.register(EmailDomain)
class EmailDomainAdmin(admin.ModelAdmin):
    pass


@admin.register(VerifiableEmail)
class VerifiableEmailAdmin(admin.ModelAdmin):
    pass
