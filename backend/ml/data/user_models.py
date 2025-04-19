from django.db.models import F, Q

from tournesol.models import ContributorRatingCriteriaScore
import solidago


DEFAULT_COMPOSITION = [
    ("direct", dict(note="uniform_gbt")),
    ("scale", dict(note="aggregated")),
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
            *args, **kwargs
        )
    
    @classmethod
    def load_user_directs(cls, directory: str, user_id=None, criterion=None) -> solidago.MultiScore:
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
            value=F("raw_score"),
        )
        init_value = pd.DataFrame(values) if len(values) > 0 else pd.DataFrame()
        init_value["left_unc"], init_value["right_unc"] = np.nan, np.nan
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
            username=F("user_id"),
            multiplier=F("scale"),
            multiplier_unc=F("scale_uncertainty"),
            translation=F("translation"),
            translation_unc=F("translation_uncertainty"),
            criterion=F("criteria"),
        )
        df = pd.DataFrame(values) if len(values) > 0 else pd.DataFrame()
        user_scales = solidago.MultiScore(cls.table_keynames["user_scales"])
        for _, row in df.iterrows():
            for kind in ("multiplier", "translation"):
                keys = row["username"], 1, kind, row["criterion"]
                user_scales[keys] = Score(row[kind], row[f"{kind}_unc"], row[f"{kind}_unc"])
        return user_scales
    
    def save(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        self.save_base_models(directory)
        self.save_user_scales(directory)
        # We do not save common scales, as it is collapsed into user scales upon saving
        return self.save_instructions(directory, json_dump)
    
    def save_base_models(self, directory: Optional[str]=None) -> str:
        """ TODO """
        raise NotImplemented
    
    def save_user_scales(self, directory: Optional[str]=None) -> str:
        """ TODO: Collapse scales of all height into a single user scale
        This should be done in Solidago rather than Tournesol """
        raise NotImplemented
    
    def save_common_scales(self, directory: Optional[str]=None) -> str:
        """ Because Tournesol's current implementation collapses all scales,
        we save common scales by saving user scales.
        Note that this is needed in LipschitzStandardize and LipschitzQuantileShift,
        which only save common scales """
        return self.save_user_scales(directory)
