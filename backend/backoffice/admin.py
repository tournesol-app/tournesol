from django.contrib import admin

from backoffice.models import TalkEntry


def link_to_youtube(obj):
    return obj.link_to_youtube()


@admin.register(TalkEntry)
class TalkEntryAdmin(admin.ModelAdmin):
    search_fields = ("title", "speakers")
    ordering = ("-date",)
    list_display = ("date", "name", "title", "link_to_youtube",  "display")
    list_display_links = ("date",)
    list_filter = ("display",)
