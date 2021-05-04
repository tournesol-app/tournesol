from django.core.management.base import BaseCommand
from backend.models import VerifiableEmail, ExpertRating, VideoRating, Video
from backend.models import DjangoUser, UserInformation, EmailDomain
from backend.rating_fields import VIDEO_FIELDS
from django.core.exceptions import ValidationError
from backend.management.commands.recompute_properties import prune_wrong_videos
from tqdm.auto import tqdm
import numpy as np


class Command(BaseCommand):
    def handle(self, **options):
        print("Computing quantiles...")
        Video.recompute_quantiles()

        print("Computing pareto optimality...")
        Video.recompute_pareto()