from django.core.management.base import BaseCommand
from backend.models import VerifiableEmail, ExpertRating, VideoRating, Video
from backend.models import DjangoUser, UserInformation, EmailDomain
from backend.rating_fields import VIDEO_FIELDS
from django.core.exceptions import ValidationError
from django.db import transaction


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
    for d in ACCEPTED_DOMAINS.strip().split('\n'):
        try:
            EmailDomain.objects.create(
                domain=d, status=EmailDomain.STATUS_ACCEPTED)
        except Exception as e:
            print(e)
            pass
    for d in REJECTED_DOMAINS.strip().split('\n'):
        try:
            EmailDomain.objects.create(
                domain=d, status=EmailDomain.STATUS_REJECTED)
        except Exception as e:
            print(e)
            pass


def recompute_property_avatar_hash(*args, **kwargs):
    for u in UserInformation.objects.all():
        try:
            hash = u.avatar_hash
            u.save()
            print("Userinfo avatar hash", hash)
        except FileNotFoundError as f:
            print("Avatar error", u, f)
        except ValidationError as f:
            print("Validation error", u, f)


def recompute_property_expertrating(*args, **kwargs):
    for u in ExpertRating.objects.all():
        try:
            ids = u.video_1_2_ids_sorted
            u.save(ignore_lastedit=True)
            print("ExpertRating ids", ids)
        except Exception as e:
            print("Error saving expert rating", e)


def prune_wrong_videos(*args, **kwargs):
    """Remove videos with wrong IDs."""
    for v in Video.objects.all():
        with transaction.atomic():
            try:
                v.full_clean()

                # to recompute the properties
                for f in Video.COMPUTED_PROPERTIES:
                    getattr(v, f)

                # to recompute the properties
                v.save()
            except ValidationError as e:
                print(f"Deleting invalid video {v}: {e}")
                v.delete()
            except Exception as e:
                print(f"Unknown error for video {v}: {e}, keeping the video")


def recompute_property_verif_email(*args, **kwargs):
    """Open all objects and save them to recompute the property."""

    for instance in VerifiableEmail.objects.all().iterator():
        try:
            val = instance.domain
            print("DOMAIN", val)
            if val:
                instance.save()
        except Exception as e:
            print("Domain error", e)


def create_emails(*args, **kwargs):
    """Create e-mails from existing users."""

    for u in DjangoUser.objects.all():
        u_inf, _ = UserInformation.objects.get_or_create(user=u)
        if not u.email:
            print(u, "No email")
            continue
        v_email, v_email_created = VerifiableEmail.objects.get_or_create(
            email=u.email, user=u_inf)
        print("Setting email for", u, v_email_created)
        v_email.user = u_inf
        v_email.is_verified = u.is_active
        v_email.save()


def nonnull_rating(*args, **kwargs):
    """Change null values to 0."""
    for v in VideoRating.objects.all():
        try:
            for f in VIDEO_FIELDS:
                if getattr(v, f) is None:
                    setattr(v, f, 0)
                    print(v, f, 0)
                v.save()
        except Exception as e:
            print(e)


def demo_account(*args, **kwargs):
    """Set demo accounts is_demo based on domain."""
    UserInformation.objects.filter(emails__domain='@tournesol.app').update(is_demo=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--cron', help='Run on cron', action='store_true')


    def handle(self, **options):

        if options['cron']:
            # only update videos
            prune_wrong_videos()

        else:
            nonnull_rating()
            fill_email_domains()
            create_emails()
            recompute_property_verif_email()
            recompute_property_expertrating()
            recompute_property_avatar_hash()
            demo_account()

            # update videos last as a downstream task
            prune_wrong_videos()