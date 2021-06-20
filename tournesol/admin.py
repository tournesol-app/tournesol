from django.contrib import admin

from .models import (Comparison)


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    pass