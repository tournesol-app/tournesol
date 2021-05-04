from django.core.management.base import BaseCommand
from backend.models import VerifiableEmail, ExpertRating, VideoRating, Video
from backend.models import DjangoUser, UserInformation, EmailDomain
from backend.rating_fields import VIDEO_FIELDS
from django.core.exceptions import ValidationError
from backend.management.commands.recompute_properties import prune_wrong_videos
from tqdm.auto import tqdm
import numpy as np


def recompute_quantiles():
    """Set {f}_quantile attribute for videos."""
    quantiles_by_feature_by_id = {f: {} for f in VIDEO_FIELDS}

    # go over all features
    print("Computing quantiles...")
    for f in tqdm(VIDEO_FIELDS):
        # order by feature (descenting, because using the top quantile)
        qs = Video.objects.filter(**{f + "__isnull": False}).order_by('-' + f)
        quantiles_f = np.linspace(0.0, 0.1, len(qs))
        for i, v in tqdm(enumerate(qs)):
            quantiles_by_feature_by_id[f][v.id] = quantiles_f[i]

    print("Writing quantiles...")
    # TODO: use batched updates with bulk_update
    for v in tqdm(Video.objects.all()):
        changed = False
        for f in VIDEO_FIELDS:
            if v.id in quantiles_by_feature_by_id[f]:
                setattr(v, f + "_quantile", quantiles_by_feature_by_id[f][v.id])
                changed = True
        if changed:
            v.save()

def recompute_pareto():
    """Compute pareto-optimality."""
    for v in tqdm(Video.objects.all()):
        new_pareto = v.get_pareto_optimal()
        if new_pareto != v.pareto_optimal:
            v.pareto_optimal = new_pareto
            v.save()

class Command(BaseCommand):
    def handle(self, **options):
        print("Computing quantiles...")
        recompute_quantiles()

        print("Computing pareto optimality...")
        # TODO: use a faster algorithm than O(|rated_videos|^2)
        prune_wrong_videos()