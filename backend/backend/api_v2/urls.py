from backend.api_v2.email_domains import EmailDomainViewSetV2
from backend.api_v2.expert_ratings import ExpertRatingsViewSetV2
from backend.api_v2.statistics import StatisticsViewSetV2
from backend.api_v2.user_information import UserInformationViewSetV2
from backend.api_v2.user_preferences import UserPreferencesViewSetV2
from backend.api_v2.video_comments import VideoCommentsViewSetV2
from backend.api_v2.video_ratings import VideoRatingsViewSetV2
from backend.api_v2.video_reports import VideoReportsViewSetV2
from backend.api_v2.videos import VideoViewSetV2
from backend.api_v2.login_signup import LoginSignupViewSetV2
from backend.api_v2.constants import ConstantsViewSetV2
from backend.api_v2.rate_later import VideoRateLaterViewSetV2


from rest_framework import routers


def fill_router(router, prefix):
    router.register(prefix + r'videos', VideoViewSetV2, basename='v2_videos')
    router.register(
        prefix + r'user_preferences',
        UserPreferencesViewSetV2,
        basename='v2_user_preferences')
    router.register(
        prefix + r'expert_ratings',
        ExpertRatingsViewSetV2,
        basename='v2_expert_ratings')
    router.register(
        prefix + r'video_ratings',
        VideoRatingsViewSetV2,
        basename='v2_video_ratings')
    router.register(
        prefix + r'video_reports',
        VideoReportsViewSetV2,
        basename='v2_video_reports')
    router.register(
        prefix + r'video_comments',
        VideoCommentsViewSetV2,
        basename='v2_video_comments')
    router.register(
        prefix + r'user_information',
        UserInformationViewSetV2,
        basename='v2_user_information')
    router.register(
        prefix + r'statistics',
        StatisticsViewSetV2,
        basename='v2_statistics')
    router.register(
        prefix + r'email_domain',
        EmailDomainViewSetV2,
        basename='v2_email_domains')
    router.register(
        prefix + r'login_signup',
        LoginSignupViewSetV2,
        basename='v2_login_signup')
    router.register(
        prefix + r'constants',
        ConstantsViewSetV2,
        basename='v2_constants')
    router.register(
        prefix + r'rate_later',
        VideoRateLaterViewSetV2,
        basename='v2_rate_later')

    return router


def make_router():
    """Create a router."""
    router = routers.DefaultRouter()
    fill_router(router, "")
    return router


router = make_router()
urlpatterns = router.urls
