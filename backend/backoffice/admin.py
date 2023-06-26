from django.contrib import admin

from backoffice.models import TalkEntry


@admin.register(TalkEntry)
class TalkEntryAdmin(admin.ModelAdmin):
    search_fields = ("title", "speakers")
    ordering = ("-date",)
    list_display = ("date", "title", "get_youtube_link", "public")
    list_display_links = ("date",)
    list_filter = ("public",)

    @admin.display(description="YouTube link")
    def get_youtube_link(self, obj):
        return obj.html_youtube_link()
