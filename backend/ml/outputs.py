import logging
from functools import cached_property
from itertools import islice
from typing import Optional

import numpy as np
import pandas as pd
from django.db import transaction
from solidago.pipeline.outputs import PipelineOutput

from core.models import User
from tournesol.models import (
    ContributorRating,
    ContributorRatingCriteriaScore,
    ContributorScaling,
    Entity,
    EntityCriteriaScore,
    EntityPollRating,
    Poll,
)
from tournesol.models.poll import ALGORITHM_MEHESTAN

logger = logging.getLogger(__name__)


class TournesolPollOutput(PipelineOutput):
    def __init__(
        self,
        poll_name: str,
        criterion: Optional[str] = None,
        save_trust_scores_enabled: bool = True,
    ):
        self.poll_name = poll_name
        self.criterion = criterion
        self.save_trust_scores_enabled = save_trust_scores_enabled

    @cached_property
    def poll(self) -> Poll:
        # Retrieving the poll instance lazily allows to use this instance
        # in a forked process (e.g with multiprocessing).
        return Poll.objects.get(name=self.poll_name)

    def save_trust_scores(self, trusts: pd.DataFrame):
        """
        `trusts`: DataFrame with
            * index:  `user_id`
            * columns: `trust_score`
        """
        if not self.save_trust_scores_enabled:
            return
        trust_scores = trusts.trust_score
        users = User.objects.filter(id__in=trust_scores.index).only("trust_score")
        for user in users:
            user.trust_score = trust_scores[user.id]
        User.objects.bulk_update(
            users,
            ["trust_score"],
            batch_size=1000
        )

    def save_individual_scalings(self, scalings: pd.DataFrame):
        scalings_iterator = (
            scalings[["s", "delta_s", "tau", "delta_tau"]]
            .replace({np.nan: None})
            .itertuples(index=True)
        )

        with transaction.atomic():
            ContributorScaling.objects.filter(poll=self.poll, criteria=self.criterion).delete()
            ContributorScaling.objects.bulk_create(
                (
                    ContributorScaling(
                        poll=self.poll,
                        criteria=self.criterion,
                        user_id=user_id,
                        scale=s,
                        scale_uncertainty=delta_s,
                        translation=tau,
                        translation_uncertainty=delta_tau,
                    )
                    for user_id, s, delta_s, tau, delta_tau in scalings_iterator
                ),
                batch_size=10000,
            )

    def save_individual_scores(
        self,
        scores: pd.DataFrame,
        single_user_id: Optional[int] = None,
    ):
        if "voting_right" not in scores:
            # Row contains `voting_right` when it comes from a full ML run, but not in the
            # case of online individual updates. As online updates do not update the
            # global scores, it makes sense to set the voting right equal to 0.0
            # temporarily and to expect it to be updated during the next ML run.
            scores["voting_right"] = 0.0

        ratings = ContributorRating.objects.filter(poll=self.poll)
        if single_user_id is not None:
            ratings = ratings.filter(user_id=single_user_id)

        rating_ids = {
            (contributor_id, entity_id): rating_id
            for rating_id, contributor_id, entity_id in ratings.values_list(
                "id", "user_id", "entity_id"
            )
        }
        ratings_to_create = set(
            (contributor_id, entity_id)
            for contributor_id, entity_id in scores[
                ["user_id", "entity_id"]
            ].itertuples(index=False)
            if (contributor_id, entity_id) not in rating_ids
        )
        ContributorRating.objects.bulk_create(
            (
                ContributorRating(
                    poll_id=self.poll.pk,
                    entity_id=entity_id,
                    user_id=contributor_id,
                )
                for contributor_id, entity_id in ratings_to_create
            ),
            batch_size=10000,
            ignore_conflicts=True,
        )
        # Refresh the `ratings_id` with the newly created `ContributorRating`s.
        rating_ids.update(
            {
                (contributor_id, entity_id): rating_id
                for rating_id, contributor_id, entity_id in ratings.values_list(
                    "id", "user_id", "entity_id"
                )
            }
        )

        scores_to_delete = ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__poll=self.poll,
            criteria=self.criterion
        )

        if single_user_id is not None:
            scores_to_delete = scores_to_delete.filter(
                contributor_rating__user_id=single_user_id
            )

        with transaction.atomic():
            scores_to_delete.delete()
            ContributorRatingCriteriaScore.objects.bulk_create(
                (
                    ContributorRatingCriteriaScore(
                        contributor_rating_id=rating_ids[(row.user_id, row.entity_id)],
                        criteria=self.criterion,
                        score=row.score,
                        uncertainty=row.uncertainty,
                        raw_score=row.raw_score,
                        raw_uncertainty=row.raw_uncertainty,
                        voting_right=row.voting_right,
                    )
                    for row in scores.itertuples()
                ),
                batch_size=10000,
            )

    def save_entity_scores(
        self,
        scores: pd.DataFrame,
        score_mode="default",
    ):
        if len(scores) == 0:
            return

        scores_iterator = scores[["entity_id", "score", "uncertainty"]].itertuples(index=False)
        with transaction.atomic():
            EntityCriteriaScore.objects.filter(
                poll=self.poll,
                score_mode=score_mode,
                criteria=self.criterion,
            ).delete()
            EntityCriteriaScore.objects.bulk_create(
                (
                    EntityCriteriaScore(
                        poll=self.poll,
                        entity_id=entity_id,
                        criteria=self.criterion,
                        score=score,
                        uncertainty=uncertainty,
                        score_mode=score_mode,
                    )
                    for entity_id, score, uncertainty in scores_iterator
                ),
                batch_size=10000,
            )


def save_tournesol_scores(poll):
    def entities_iterator():
        for entity in (
            Entity.objects.filter(all_criteria_scores__poll=poll)
            .distinct()
            .with_prefetched_scores(poll_name=poll.name)
            .with_prefetched_poll_ratings(poll_name=poll.name)
        ):
            if poll.algorithm == ALGORITHM_MEHESTAN:
                # The Tournesol score is the score of the main criterion.
                tournesol_score = next(
                    (
                        s.score
                        for s in entity.criteria_scores
                        if s.criteria == poll.main_criteria
                    ),
                    None,
                )
            else:
                tournesol_score = 10 * sum(
                    criterion.score for criterion in entity.criteria_scores
                )

            poll_rating = entity.single_poll_rating
            if poll_rating is None:
                logger.warning(
                    "Entity had not EntityPollRating to save tournesol_score. "
                    "It will be created now."
                )
                poll_rating = EntityPollRating.objects.create(poll=poll, entity=entity)
                entity.single_poll_ratings = [poll_rating]

            poll_rating.tournesol_score = tournesol_score
            yield entity

    # Updating all entities at once increases the risk of a database deadlock.
    # We use explicit batches instead of bulk_update "batch_size" to avoid
    # locking all entities in a large transaction.
    entities_it = entities_iterator()
    while batch := list(islice(entities_it, 1000)):
        EntityPollRating.objects.bulk_update(
            [ent.single_poll_rating for ent in batch],
            fields=["tournesol_score"],
        )
