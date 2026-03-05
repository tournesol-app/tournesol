from copy import deepcopy
from typing import Iterable

from solidago.poll import *
from solidago.poll.scoring import *


class Filtering:
    def __init__(self,
        usernames: str | Iterable[str] | None = None,
        entity_names: str | Iterable[str] | None = None,
        criteria: str | Iterable[str] | None = None,
    ):
        self.usernames = {usernames} if isinstance(usernames, str) else usernames
        self.entity_names = {entity_names} if isinstance(entity_names, str) else entity_names
        self.criteria = {criteria} if isinstance(criteria, str) else criteria

    def fn(self, poll: Poll) -> Poll:
        return Poll(
            self._get_users(poll.users),
            self._get_entities(poll.entities),
            self._get_vouches(poll.vouches),
            self._get_public_settings(poll.public_settings),
            self._get_ratings(poll.ratings),
            self._get_comparisons(poll.comparisons),
            self._get_voting_rights(poll.voting_rights),
            self._get_user_models(poll.user_models),
            self._get_global_model(poll.global_model),
        )

    def _get_users(self, users: Users) -> Users:
        if self.usernames is None:
            return deepcopy(users)
        return Users(users.df[users.df.index.isin(self.usernames)])
    
    def _get_entities(self, entities: Entities) -> Entities:
        if self.entity_names is None:
            return deepcopy(entities)
        return Entities(entities.df[entities.df.index.isin(self.entity_names)])
    
    def _get_vouches(self, vouches: Vouches) -> Vouches:
        if self.usernames is None:
            return deepcopy(vouches)
        df = vouches.df
        df = df[df.by.isin(self.usernames) & df.to.isin(self.usernames)]
        return Vouches(df)
    
    def _get_public_settings(self, public_settings: PublicSettings) -> PublicSettings:
        df = public_settings.df
        if self.usernames is not None:
            df = df[df.username.isin(self.usernames)]
        if self.entity_names is not None:
            df = df[df.entity_name.isin(self.entity_names)]
        return PublicSettings(df)
    
    def _get_ratings(self, ratings: Ratings) -> Ratings:
        df = ratings.df
        if self.usernames is not None:
            df = df[df.username.isin(self.usernames)]
        if self.entity_names is not None:
            df = df[df.entity_name.isin(self.entity_names)]
        if self.criteria is not None:
            df = df[df.criterion.isin(self.criteria)]
        return Ratings(df)
    
    def _get_comparisons(self, comparisons: Comparisons) -> Comparisons:
        df = comparisons.df
        if self.usernames is not None:
            df = df[df.username.isin(self.usernames)]
        if self.entity_names is not None:
            df = df[df.left_name.isin(self.entity_names) & df.right_name.isin(self.entity_names)]
        if self.criteria is not None:
            df = df[df.criterion.isin(self.criteria)]
        return Comparisons(df)
    
    def _get_voting_rights(self, voting_rights: VotingRights) -> VotingRights:
        df = voting_rights.df
        if self.usernames is not None:
            df = df[df.username.isin(self.usernames)]
        if self.entity_names is not None:
            df = df[df.entity_name.isin(self.entity_names)]
        if self.criteria is not None:
            df = df[df.criterion.isin(self.criteria)]
        return VotingRights(df)

    def _get_user_models(self, user_models: UserModels) -> UserModels:
        user_directs_df = user_models.user_directs.df
        user_categories_df = user_models.user_categories.df
        user_parameters_df = user_models.user_parameters.df
        user_multipliers_df = user_models.user_multipliers.df
        user_translations_df = user_models.user_translations.df
        common_multipliers_df = user_models.common_multipliers.df
        common_translations_df = user_models.common_translations.df
        
        if self.usernames is not None:
            user_directs_df = user_directs_df[user_directs_df.username.isin(self.usernames)]
            user_categories_df = user_categories_df[user_categories_df.username.isin(self.usernames)]
            user_parameters_df = user_parameters_df[user_parameters_df.username.isin(self.usernames)]
            user_multipliers_df = user_multipliers_df[user_multipliers_df.username.isin(self.usernames)]
            user_translations_df = user_translations_df[user_translations_df.username.isin(self.usernames)]

        if self.entity_names is not None:
            user_directs_df = user_directs_df[user_directs_df.entity_name.isin(self.entity_names)]
        
        if self.criteria is not None:
            user_directs_df = user_directs_df[user_directs_df.criterion.isin(self.criteria)]
            user_categories_df = user_categories_df[user_categories_df.criterion.isin(self.criteria)]
            user_parameters_df = user_parameters_df[user_parameters_df.criterion.isin(self.criteria)]
            user_multipliers_df = user_multipliers_df[user_multipliers_df.criterion.isin(self.criteria)]
            user_translations_df = user_translations_df[user_translations_df.criterion.isin(self.criteria)]
            common_multipliers_df = common_multipliers_df[common_multipliers_df.criterion.isin(self.criteria)]
            common_translations_df = common_translations_df[common_translations_df.criterion.isin(self.criteria)]
        
        return UserModels(
            user_models.default_composition,
            {
                username: composition for username, composition in user_models.user_compositions.items() 
                if self.usernames is None or username in self.usernames
            },
            UserDirectScores(user_directs_df),
            UserCategoryScores(user_categories_df),
            UserParameters(user_parameters_df),
            UserMultipliers(user_multipliers_df),
            UserTranslations(user_translations_df),
            CommonMultipliers(common_multipliers_df),
            CommonTranslations(common_translations_df),
        )
    
    def _get_global_model(self, global_model: ScoringModel) -> ScoringModel:
        directs_df = global_model.directs.df
        categories_df = global_model.categories.df
        parameters_df = global_model.parameters.df
        multipliers_df = global_model.multipliers.df
        translations_df = global_model.translations.df

        if self.entity_names is not None:
            directs_df = directs_df[directs_df.entity_name.isin(self.entity_names)]
        
        if self.criteria is not None:
            directs_df = directs_df[directs_df.criterion.isin(self.criteria)]
            categories_df = categories_df[categories_df.criterion.isin(self.criteria)]
            parameters_df = parameters_df[parameters_df.criterion.isin(self.criteria)]
            multipliers_df = multipliers_df[multipliers_df.criterion.isin(self.criteria)]
            translations_df = translations_df[translations_df.criterion.isin(self.criteria)]
        
        return ScoringModel(
            global_model.composition,
            DirectScores(directs_df),
            CategoryScores(categories_df),
            Parameters(parameters_df),
            Multipliers(multipliers_df),
            Translations(translations_df),
        )