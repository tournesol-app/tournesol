import logging

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments
from solidago.voting_rights import VotingRights
from solidago.scoring_model import ScoringModel

from solidago.trust_propagation import TrustPropagation
from solidago.trust_propagation.lipschitrust import LipschiTrust
from solidago.voting_rights_assignment import VotingRightsAssignment
from solidago.voting_rights_assignment.affine_overtrust import AffineOvertrust
from solidago.preference_learning import PreferenceLearning
from solidago.preference_learning.generalized_bradley_terry import UniformGBT
from solidago.scaling import Scaling, ScalingCompose
from solidago.scaling.mehestan import Mehestan
from solidago.scaling.quantile_zero_shift import QuantileZeroShift
from solidago.aggregation import Aggregation
from solidago.aggregation.standardized_qrmed import QuantileStandardizedQrMedian
from solidago.post_process import PostProcess
from solidago.post_process.squash import Squash

logger = logging.getLogger(__name__)


@classdata
class DefaultPipeline:
    """ Instantiates the default pipeline described in
    "Solidago: A Modular Pipeline for Collaborative Scaling".
    """
    trust_propagation: TrustPropagation = LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    )
    voting_rights: VotingRights = VotingRightsWithLimitedOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    )
    preference_learning: PreferenceLearning = UniformGBT(
        prior_std_dev=7,
        comparison_max=10,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
        initialization=dict()
    )
    scaling: Scaling = ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_n_judged_entities=10,
            n_scalers_max=1000,
            error=1e-5
        ),
        QuantileZeroShift(
            zero_quantile=0.15,
            lipschitz=0.1,
            error=1e-5
        )
    )
    aggregation: Aggregation = QuantileStandardizedQrMedian(
        dev_quantile=0.9,
        lipschitz=0.1,
        error=1e-5
    )
    post_process: PostProcess = Squash(
        score_max=100
    )


class Pipeline:
    def __init__(
        self,
        trust_propagation: TrustPropagation = DefaultPipeline.trust_propagation,
        voting_rights: VotingRights = DefaultPipeline.voting_rights,
        preference_learning: PreferenceLearning = DefaultPipeline.preference_learning,
        scaling: Scaling = DefaultPipeline.scaling,
        aggregation: Aggregation = DefaultPipeline.aggregation,
        post_process: PostProcess = DefaultPipeline.post_process
    ):
        """ Instantiates the pipeline components.
        
        Parameters
        ----------
        trust_propagation: TrustPropagation
            Algorithm to spread trust based on pretrusts and vouches
        voting_rights: VotingRights
            Algorithm to assign voting rights to each user
        preference_learning: PreferenceLearning
            Algorithm to learn a user model based on each user's data
        scaling: Scaling
            Algorithm to put user models on a common scale
        aggregation: Aggregation
            Algorithm to aggregate the different users' models
        post_process: PostProcess
            Algorithm to post-process user and global models,
            and make it readily usable for applications.
        """
        self.trust_propagation = trust_propagation
        self.voting_rights = voting_rights
        self.preference_learning = preference_learning
        self.scaling = scaling
        self.aggregation = aggregation
        self.post_process = post_process
        
    def __call__(
        self,
        pretrusts: pd.DataFrame,
        vouches: pd.DataFrame,
        entities: pd.DataFrame,
        privacy: PrivacySettings,
        judgments: Judgments
    ) -> tuple[pd.DataFrame, VotingRights, dict[int, ScoringModel], ScoringModel]:
        """ Run Pipeline 
        
        Parameters
        ----------
        pretrusts: DataFrame with columns
            * user_id: int (index)
            * is_pretrusted: bool
        vouches: DataFrame with columns
            * voucher (int)
            * vouchee (int)
            * vouch (float)
        entities: DataFrame with columns
            * entity_id: int (index)
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }
        judgments: Jugdments
            judgments[user] must yield the judgment data provided by the user
            
        Returns
        -------
        trusts: DataFrame with columns
            * user_id: int (index)
            * is_pretrusted: bool
            * trust_score: float
        voting_rights: VotingRights
            voting_rights[user, entity] is the user's voting right for entity
        user_models: list[UserModel]
            user_models[user] is the user's model
        global_model: GlobalModel
            global model
        """
        if criterion is None:
            criterion = set(data.comparisons["criteria"])
        if type(criterion) in (set, list, tuple):
            return { c: self(dataset, c) for c in criterion }
        
        logger.info("Starting the full Solidago pipeline for criterion '%s'", criterion)
        
        logger.info(f"Pipeline 1. Propagating trust with {self.trust_propagation}")
        trusts = self.trust_propagation(pretrusts, vouches)
        
        logger.info(f"Pipeline 2. Computing voting rights with {self.voting_rights}")
        voting_rights = self.voting_rights(trusts, vouches, privacy, judgments)
    
        logger.info(f"Pipeline 3. Computing user models with {self.preference_learning}")
        user_models = dict()
        for user, _ in users.iterrows():
            logger.info(f"    Pipeline 3.{user}. Learning user {user}'s model")
            user_models[user] = self.preference_learning(judgments[user], entities)
        
        logger.info(f"Pipeline 4. Collaborative score scaling with {self.scaling}")
        user_models = self.scaling(user_models, users, entities, voting_rights, privacy)
        
        logger.info(f"Pipeline 5. Score aggregation with {self.aggregation}")
        user_models, global_model = self.aggregation(voting_rights, user_models, users, entities)
                
        logger.info(f"Pipeline 6. Post-processing scores {self.post_process}")
        user_models, global_model = self.post_process(user_models, global_model, entities)
        
        return trusts, voting_rights, user_models, global_model
