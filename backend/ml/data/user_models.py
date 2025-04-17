from django.db.models import F, Q

from tournesol.models import ContributorRatingCriteriaScore
import solidago


DEFAULT_COMPOSITION = [
    ("direct", dict(note="uniform_gbt")),
    ("scale", dict(note="mehestan")),
    ("scale", dict(note="lipschitz_standardize")),
    ("scale", dict(note="lipschitz_quantile_shift")),
    ("squash", dict(score_max=100, note="squash")),
]

class UserModels(solidago.UserModels):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def load(cls, 
        directory: str, 
        default_composition: list=DEFAULT_COMPOSITION, 
        *args, **kwargs
    ) -> "UserModels":
        return cls(
            user_directs=cls.load_user_directs(directory),
            user_scales=cls.load_user_scales(directory),
            common_scales=cls.load_common_scales(directory),
            *args, **kwargs
        )
    
    @classmethod
    def load_user_directs(cls, directory: str, user_id=None, criterion=None) -> solidago.MultiScore:
        """ TODO: Left and right uncertainties? """
        scores_queryset = ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__poll__name=directory,
            contributor_rating__user__is_active=True,
        )
        if criterion is not None:
            scores_queryset = scores_queryset.filter(criteria=criterion)
        if user_id is not None:
            scores_queryset = scores_queryset.filter(contributor_rating__user_id=user_id)

        values = scores_queryset.values(
            criterion=F("criteria"),
            entity_name=F("contributor_rating__entity_id"),
            username=F("contributor_rating__user_id"),
            value="score",
            left_unc=F("left_uncertainty"),
            right_unc=F("right_uncertainty"),
        )
        init_value = pd.DataFrame(values) if len(values) > 0 else None
        # keynames == ("username", "entity_name", "criterion")
        return solidago.MultiScore(cls.table_keynames["user_directs"], init_value)

    @classmethod
    def load_user_scales(cls, directory: str, user_id=None) -> solidago.MultiScore:
        """ TODO Fetch saved individual scalings
        Returns:
        - ratings_df: DataFrame with columns
            * `user_id`: int
            * `criterion`: str
            * `scale`: float
            * `scale_uncertainty`: float
            * `translation`: float
            * `translation_uncertainty`: float
        """
        scalings = ContributorScaling.objects.filter(poll__name=directory)
        if user_id is not None:
            scalings = scalings.filter(user_id=user_id)
        values = scalings.values(
            username="user_id",
            "scale",
            "scale_uncertainty",
            "translation",
            "translation_uncertainty",
            criterion=F("criteria"),
        )
        # TODO : Change columns to match ("username", "height", "kind", "criterion")
        init_data = pd.DataFrame(values) if len(values) > 0 else None
        return solidago.MultiScore(cls.table_keynames["user_scales"], init_data)
    
    @classmethod
    def load_common_scales(cls, directory: str) -> solidago.MultiScore:
        """ TODO """
        # TODO : Change columns to match ("height", "kind", "criterion")
        raise NotImplemented
    
    def save(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        self.save_base_models(directory)
        self.save_user_scales(directory)
        self.save_common_scales(directory)
        return self.save_instructions(directory, json_dump)
    
    def save_base_models(self, directory: Optional[str]=None) -> str:
        """ TODO """
        raise NotImplemented
    
    def save_user_scales(self, directory: Optional[str]=None) -> str:
        """ TODO """
        raise NotImplemented
    
    def save_common_scales(self, directory: Optional[str]=None) -> str:
        """ TODO """
        raise NotImplemented
