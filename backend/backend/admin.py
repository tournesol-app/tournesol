from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import Case, When, Value, IntegerField

from .models import Video, UserPreferences, ExpertRating, RepresentativeModelUsage
from .models import VideoComment, VideoCommentMarker, Degree, VerifiableEmail, VideoSelectorSkips
from .models import VideoRating, UserInformation, Expertise, ExpertiseKeyword, EmailDomain
from .models import ResetPasswordToken, ExpertRatingSliderChanges, VideoRatingThankYou
from .models import VideoRatingPrivacy, VideoRateLater


admin.site.register(Video)
admin.site.register(UserPreferences)
admin.site.register(ExpertRating, SimpleHistoryAdmin)
admin.site.register(VideoComment)
admin.site.register(VideoCommentMarker)
admin.site.register(VideoRating)
admin.site.register(UserInformation)
admin.site.register(Expertise)
admin.site.register(ExpertiseKeyword)
admin.site.register(Degree)
admin.site.register(VerifiableEmail)
admin.site.register(RepresentativeModelUsage)
admin.site.register(VideoSelectorSkips)
admin.site.register(ResetPasswordToken)
admin.site.register(ExpertRatingSliderChanges)
admin.site.register(VideoRatingThankYou)
admin.site.register(VideoRatingPrivacy)
admin.site.register(VideoRateLater)


@admin.register(EmailDomain)
class EmailDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "status", "datetime_add", "is_pending")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _is_pending=Case(
                When(status=EmailDomain.STATUS_PENDING,
                     then=Value(1)),
                default=Value(0),
                output_field=IntegerField())
        )
        return queryset

    def is_pending(self, obj):
        return obj._is_pending

    is_pending.admin_order_field = '_is_pending'
