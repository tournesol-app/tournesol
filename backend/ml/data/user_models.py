import solidago


class UserModels(solidago.UserModels):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_user_scalings(self, user_id=None) -> pd.DataFrame:
        """Fetch saved invidiual scalings
        Returns:
        - ratings_df: DataFrame with columns
            * `user_id`: int
            * `criterion`: str
            * `scale`: float
            * `scale_uncertainty`: float
            * `translation`: float
            * `translation_uncertainty`: float
        """

        scalings = ContributorScaling.objects.filter(poll__name=self.poll_name)
        if user_id is not None:
            scalings = scalings.filter(user_id=user_id)
        values = scalings.values(
            "user_id",
            "scale",
            "scale_uncertainty",
            "translation",
            "translation_uncertainty",
            criterion=F("criteria"),

        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "criterion",
                    "scale",
                    "scale_uncertainty",
                    "translation",
                    "translation_uncertainty",
                ]
            )
        return pd.DataFrame(values)

    def get_individual_scores(
        self, user_id: Optional[int] = None, criterion: Optional[str] = None,
    ) -> pd.DataFrame:
        scores_queryset = ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__poll__name=self.poll_name,
            contributor_rating__user__is_active=True,
        )
        if criterion is not None:
            scores_queryset = scores_queryset.filter(criteria=criterion)
        if user_id is not None:
            scores_queryset = scores_queryset.filter(contributor_rating__user_id=user_id)

        values = scores_queryset.values(
            "raw_score",
            criterion=F("criteria"),
            entity_id=F("contributor_rating__entity_id"),
            user_id=F("contributor_rating__user_id"),
        )
        if len(values) == 0:
            return pd.DataFrame(columns=["user_id", "entity_id", "criterion", "raw_score"])

        dtf = pd.DataFrame(values)
        return dtf[["user_id", "entity_id", "criterion", "raw_score"]]
