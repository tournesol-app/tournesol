from backend.models import DjangoUser, UserPreferences, EmailDomain, \
    UserInformation, VerifiableEmail, Video, ExpertRating, VideoRatingPrivacy
from frontend.views import create_user_preferences
import numpy as np
from backend.models import VIDEO_FIELDS


def create_toy_data():
    DjangoUser.objects.create_user(username='test', is_active=True)
    DjangoUser.objects.create_user(username='test1', is_active=True)
    DjangoUser.objects.create_user(username='test2', is_active=True)
    create_user_preferences()

    EmailDomain.objects.create(domain="@accepted.com", status=EmailDomain.STATUS_ACCEPTED)
    EmailDomain.objects.create(domain="@rejected.com", status=EmailDomain.STATUS_REJECTED)
    EmailDomain.objects.create(domain="@pending.com", status=EmailDomain.STATUS_PENDING)

    up = UserPreferences.objects.get(user__username='test')
    up1 = UserPreferences.objects.get(user__username='test1')
    up2 = UserPreferences.objects.get(user__username='test2')

    ui = UserInformation.objects.get(user__username='test')
    ui1 = UserInformation.objects.get(user__username='test1')
    ui2 = UserInformation.objects.get(user__username='test2')

    VerifiableEmail.objects.create(email="test@accepted.com", user=ui1)
    VerifiableEmail.objects.create(email="test@rejected.com", user=ui2)

    v1 = Video.objects.create(video_id='v1')
    v2 = Video.objects.create(video_id='v2')
    v3 = Video.objects.create(video_id='v3')
    v4 = Video.objects.create(video_id='v4')

    ExpertRating.objects.create(user=up1, video_1=v1, video_2=v2,
                                **{f: np.random.rand() * 100 for f in VIDEO_FIELDS})
    ExpertRating.objects.create(user=up1, video_1=v1, video_2=v3,
                                **{f: np.random.rand() * 100 for f in VIDEO_FIELDS})
    ExpertRating.objects.create(user=up1, video_1=v1, video_2=v4,
                                **{f: np.random.rand() * 100 for f in VIDEO_FIELDS})
    ExpertRating.objects.create(user=up, video_1=v1, video_2=v4,
                                **{f: np.random.rand() * 100 for f in VIDEO_FIELDS})
    ExpertRating.objects.create(user=up2, video_1=v1, video_2=v4,
                                **{f: np.random.rand() * 100 for f in VIDEO_FIELDS})

    VideoRatingPrivacy.objects.create(user=up1, video=v1, is_public=True)
    VideoRatingPrivacy.objects.create(user=up1, video=v2, is_public=True)
    VideoRatingPrivacy.objects.create(user=up1, video=v3, is_public=True)
    VideoRatingPrivacy.objects.create(user=up2, video=v3, is_public=False)
    VideoRatingPrivacy.objects.create(user=up2, video=v4, is_public=False)
