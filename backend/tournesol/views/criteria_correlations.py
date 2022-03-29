
import numpy as np
from django.http import JsonResponse
from rest_framework.generics import GenericAPIView
from scipy.stats import linregress

from tournesol.models.poll import Poll
from tournesol.models.ratings import ContributorRating


def compute_correlation(scores_1: dict, scores_2: dict) -> int:
    """
    inputs are dictionaries with entities as keys and scores as values
    for a given user and a given rating criteria
    """

    # At least two datapoints are necessary to compute correlations
    if sum(entity in scores_1 for entity in scores_2) > 1:
        h = np.corrcoef(
            [scores_1[e] for e in scores_1 if e in scores_2],
            [scores_2[e] for e in scores_1 if e in scores_2],
        )
        return None if np.isnan(h[0][1]) else h[0][1] 
    else:
        return None


def compute_slope(scores_1: dict, scores_2: dict) -> int:
    """ 
    inputs are dictionaries with entities as keys and scores as values
    for a given user and a given rating criteria
    """

    # At least two datapoints are necessary to compute slopes
    if sum(entity in scores_1 for entity in scores_2) > 1:
        return linregress(
            [scores_1[e] for e in scores_1 if e in scores_2],
            [scores_2[e] for e in scores_1 if e in scores_2],
        ).slope
    else:
        return None

class ContributorCriteriaCorrelationsView(GenericAPIView):
    
    def get(self, request, poll_name):
        poll = Poll.objects.get(name=poll_name)
        criterias = poll.criterias_list
        n = len(criterias)

        ratings = ContributorRating.objects.prefetch_related("criteria_scores").filter(user=request.user)

        scores = {criteria: {} for criteria in criterias}
        for r in ratings:
            for s in r.criteria_scores.all():
                scores[s.criteria][r.entity] = s.score

        

        return JsonResponse({
            "criterias": criterias,
            "correlations": [
                [compute_correlation(scores[c1], scores[c2]) for c1 in criterias]
                for c2 in criterias
            ],
            "slopes": [
                [compute_slope(scores[c1], scores[c2]) for c1 in criterias]
                for c2 in criterias
            ],
        })