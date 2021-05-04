from django.core.management.base import BaseCommand
from backend.models import VerifiableEmail, ExpertRating, VideoRating, Video
from backend.models import DjangoUser, UserInformation, EmailDomain
from backend.rating_fields import VIDEO_FIELDS
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from tqdm.auto import tqdm


ACCEPTED_DOMAINS = """
@epfl.ch
@edu-vd.ch
@edu.ge.ch
@edu.vs.ch
@edu.jura.ch
@rpn.ch
@polytechnique.edu
@harvard.edu
@mit.edu
@polymtl.ca
@stanford.edu
@cs.berkeley.edu
@insa-lyon.fr
@ens-lyon.fr
@ens-paris-saclay.fr
@centralesupelec.fr
@cornell.edu
@cs.mcgill.ca
@uqam.ca
@lemonde.fr
@animath.fr
@acfas.ca
"""

REJECTED_DOMAINS = """
@gmail.com
@hotmail.com
@yahoo.com
"""


def fill_email_domains(*args, **kwargs):
    """Open all objects and save them to recompute the property."""
    for d in tqdm(ACCEPTED_DOMAINS.strip().split('\n')):
        try:
            EmailDomain.objects.create(
                domain=d, status=EmailDomain.STATUS_ACCEPTED)
        except Exception as e:
            print(e)
            pass
    for d in tqdm(REJECTED_DOMAINS.strip().split('\n')):
        try:
            EmailDomain.objects.create(
                domain=d, status=EmailDomain.STATUS_REJECTED)
        except Exception as e:
            print(e)
            pass


def recompute_property_avatar_hash(*args, **kwargs):
    for u in tqdm(UserInformation.objects.all()):
        try:
            getattr(u, 'avatar_hash')
            u.save()
        except FileNotFoundError as f:
            print("Avatar error", u, f)
        except ValidationError as f:
            print("Validation error", u, f)


def recompute_property_expertrating(*args, **kwargs):
    for u in tqdm(ExpertRating.objects.filter(video_1_2_ids_sorted=None)):
        try:
            prop = getattr(u, 'video_1_2_ids_sorted')
            ExpertRating.objects.filter(pk=u.pk).update(video_1_2_ids_sorted=prop)
        except Exception as e:
            print("Error saving expert rating", e)


def prune_wrong_videos(*args, **kwargs):
    """Remove videos with wrong IDs."""
    for v in tqdm(Video.objects.all()):
        try:
            v.full_clean()
        except ValidationError as e:
            print(f"Deleting invalid video {v}: {e}")
            v.delete()
        except Exception as e:
            print(f"Unknown error for video {v}: {e}, keeping the video")


def recompute_property_verif_email(*args, **kwargs):
    """Open all objects and save them to recompute the property."""

    for instance in tqdm(VerifiableEmail.objects.filter(domain_fk=None).iterator()):
        try:
            val = instance.domain
            if val:
                instance.save()
        except Exception as e:
            print("Domain error", e)


def create_emails(*args, **kwargs):
    """Create e-mails from existing users."""

    # creating emails only for those who don't have any
    qs = DjangoUser.objects.all().annotate(_n_emails=Count('userinformation__emails',
                                           filter=Q(userinformation__emails__is_verified=True)))
    qs = qs.filter(_n_emails=0, email__isnull=False)

    for u in tqdm(qs):
        u_inf, _ = UserInformation.objects.get_or_create(user=u)
        if not u.email:
            print(u, "No email")
            continue
        v_email, _ = VerifiableEmail.objects.get_or_create(
            email=u.email, user=u_inf)
        # print("Setting email for", u, v_email_created)
        v_email.user = u_inf
        v_email.is_verified = u.is_active
        v_email.save()


def nonnull_rating(*args, **kwargs):
    """Change null values to 0."""

    for f in tqdm(VIDEO_FIELDS):
        qs = VideoRating.objects.all().filter(**{f: None})
        qs.update(**{f: 0.0})


def demo_account(*args, **kwargs):
    """Set demo accounts is_demo based on domain."""
    UserInformation.objects.filter(emails__domain='@tournesol.app').update(is_demo=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--cron', help='Run on cron', action='store_true')
        parser.add_argument('--set_all_pending', help="Set all videos as needing an update",
                            action='store_true')

    def handle(self, **options):

        if options['set_all_pending']:
            Video.objects.all().update(is_update_pending=True)
        elif options['cron']:
            # only update videos
            Video.recompute_computed_properties(only_pending=True)

        else:
            print("Non-null ratings...")
            nonnull_rating()

            print("Email domains...")
            fill_email_domains()

            print("Creating emails...")
            create_emails()

            print("Email verif...""")
            recompute_property_verif_email()

            print("Ratings...")
            recompute_property_expertrating()

            print("Avatar hashes...")
            recompute_property_avatar_hash()

            print("Demo accounts...")
            demo_account()

            # update videos last as a downstream task
            # print("Wrong videos...")
            # prune_wrong_videos()

            # recomputing properties
            # done via the cron job, otherwise will take too much time for the update...
            # print("Video props...")
            # Video.recompute_computed_properties(only_pending=True)
