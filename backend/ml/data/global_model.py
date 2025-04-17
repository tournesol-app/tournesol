from django.db.models import F, Q

import solidago
from tournesol.models import EntityCriteriaScore


DEFAULT_COMPOSITION = [
    ("direct", dict(note="qr_quantile")),
    ("squash", dict(score_max=100, note="squash")),
]

class GlobalModel(solidago.ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, 
        directory: str, 
        composition: list=DEFAULT_COMPOSITION, 
        criterion=None, 
        *args, **kwargs
    ) -> "GlobalModel":
        scores_queryset = EntityCriteriaScore.objects.filter(
            entity_criteria_score__poll__name=directory,
        )
        if criterion is not None:
            scores_queryset = scores_queryset.filter(criteria=criterion)

        values = scores_queryset.values(
            entity_name=F("contributor_rating__entity_id"),
            criterion=F("criteria"),
            value=F("raw_score"),
            left_unc=F("left_uncertainty"),
            right_unc=F("right_uncertainty"),
        )
        # keynames == ("entity_name", "criterion")
        directs = solidago.MultiScore(cls.table_keynames["directs"], pd.DataFrame(values))
        return cls(composition, directs)

    def save(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        poll = Poll.objects.get(name=directory)
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