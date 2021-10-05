"""
Defines Admin interface for Tournesol's core app
"""

from django.contrib import admin
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
class UserAdmin(admin.ModelAdmin):
    pass


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
