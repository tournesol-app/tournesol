from django.core.management.base import BaseCommand
from backend.models import VideoRating, UserPreferences, VideoRatingPrivacy, Video
from django.db.models import Count, Q


class Command(BaseCommand):
    """For existing ratings without privacy status, set it."""
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--set_public', help='Set public (True) or private (False) status',
                            type=bool, default=False)
        parser.add_argument('--dry_run', help="Do not make any changes", action='store_true')

    def handle(self, **options):
        is_public = options['set_public']
        print(f"Setting all ambiguous rating privacys to PUBLIC={is_public}")

        for user in UserPreferences.objects.all():
            # ratings by user without privacy settings
            qs = VideoRating.objects.filter(user=user)
            qs = qs.annotate(_n_privacys=Count('video__videoratingprivacy',
                                               distinct=True,
                                               filter=Q(video__videoratingprivacy__user=user)))
            qs = qs.filter(_n_privacys=0)

            video_ids = [x[0] for x in qs.values_list('video__video_id')]

            print(f"User {user} has the following ambiguous privacy settings: {video_ids}")

            videos = [Video.objects.get(video_id=vid) for vid in video_ids]

            objs = [VideoRatingPrivacy(user=user, video=video, is_public=is_public)
                    for video in videos]

            if not options['dry_run']:
                VideoRatingPrivacy.objects.bulk_create(objs)

            print(f"Objects for {user}: {objs}")
