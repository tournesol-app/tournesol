from django.contrib import admin

from backoffice.models import TalkEntry


@admin.register(TalkEntry)
class TalkEntryAdmin(admin.ModelAdmin):
    search_fields = ("title", "speakers")
    ordering = ("-date",)
    list_display = ("date", "name", "title", "youtube_link",  "display")
    list_display_links = ("date",)
    list_filter = ("display",)
