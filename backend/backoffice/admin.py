from django.contrib import admin

from backoffice.models import TalkEntry


@admin.register(TalkEntry)
class TalkEntryAdmin(admin.ModelAdmin):
    search_fields = ("name", "title")
    ordering = ("name", "date", "title")
    list_display = ("name", "date", "title")
    list_display_links = ("name", "date", "title")

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        return qst
