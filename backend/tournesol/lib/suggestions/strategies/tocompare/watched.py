import random

from tournesol.lib.suggestions.strategies.tocompare.classic import ClassicEntitySuggestionStrategy
from tournesol.models import ContributorRating, RateLater
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT


class WatchedEntitySuggestionStrategy(ClassicEntitySuggestionStrategy):
    """
    A variation of the strategy `ClassicEntitySuggestionStrategy` that
    suggests in priority entities that have been watched/consumed/understood.
    """

    # The expected number of entities retrieved from each pool. The sum should
    # match the `max_suggestions`.
    sample_size_compared = 13
    sample_size_rate_later = 7
    sample_size_reco_last_month = 0

    def _ids_from_pool_compared(self) -> list[int]:
        poll = self.poll
        user = self.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        compared = (
            ContributorRating.objects.filter(poll=poll, user=user, entity_seen=True)
            .select_related("entity")
            .annotate_n_comparisons()
            .filter(n_comparisons__lt=max_threshold)
            .filter(n_comparisons__gt=0)
            .values_list("entity_id", flat=True)
        )

        return random.sample(
            # not a cryptographic use # nosec B311
            list(compared),
            min(len(compared), self.max_suggestions),
        )

    def _ids_from_pool_rate_later(self, exclude_ids: list[int]) -> list[int]:
        poll = self.poll
        user = self.user

        # Prevent Django.db.utils.ProgrammingError when `exclude_ids` is
        # empty:
        #
        #    AND rate_later.entity_id NOT IN ()
        #                                     ^
        if not exclude_ids:
            exclude_ids.append(-1)

        results = RateLater.objects.raw(
            """
            SELECT
              rate_later.id,
              rate_later.entity_id

            FROM tournesol_ratelater rate_later

            JOIN tournesol_contributorrating
              ON tournesol_contributorrating.poll_id = rate_later.poll_id
             AND tournesol_contributorrating.user_id = rate_later.user_id
             AND tournesol_contributorrating.entity_id = rate_later.entity_id

            WHERE rate_later.poll_id = %(poll_id)s
              AND rate_later.user_id = %(user_id)s
              AND tournesol_contributorrating.entity_seen = true

              AND rate_later.entity_id NOT IN %(exclude_ids)s
          """,
            {"poll_id": poll.id, "user_id": user.id, "exclude_ids": tuple(exclude_ids)},
        )

        samples = random.sample(
            # not a cryptographic use # nosec B311
            list(results),
            min(len(results), self.max_suggestions),
        )

        return [sample.id for sample in samples]

    def get_results(self):
        return self.get_results_for_user_intermediate()
