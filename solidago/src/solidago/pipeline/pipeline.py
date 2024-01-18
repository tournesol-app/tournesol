import logging

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments
from solidago.voting_rights import VotingRights
from solidago.user_model import UserModel
from solidago.global_model import GlobalModel

from solidago.trust_propagation import TrustPropagation
from solidago.trust_propagation.lipschitrust import LipschiTrust
from solidago.voting_rights_assignment import VotingRightsAssignment
from solidago.voting_rights_assignment.limited_overtrust import VotingRightsWithLimitedOvertrust
from solidago.user_models_inference import UserModelInference
from solidago.user_models_inference.generalized_bradley_terry import UniformGBT
from solidago.scaling import Scaling, ScalingCompose
from solidago.scaling.mehestan import Mehestan
from solidago.scaling.quantile_zero_shift import QuantileZeroShift
from solidago.aggregation import Aggregation
from solidago.aggregation.standardized_qrmed import QuantileStandardizedQrMed
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
    user_model_inference: UserModelInference = UniformGBT(
        comparison_max=10
    )
    scaling: Scaling = ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_comparison=10,
            n_scalers_max=1000
        ),
        QuantileZeroShift(
            zero_quantile=0.15
        )
    )
    aggregation: Aggregation = QuantileStandardizedQrMed(
        qtl_std_dev=0.9,
        lipschitz=0.1
    )
    post_process: PostProcess = Squash()


class Pipeline:
    def __init__(
        self,
        trust_propagation: TrustPropagation = DefaultPipeline.trust_propagation,
        voting_rights: VotingRights = DefaultPipeline.voting_rights,
        user_model_inference: UserModelInference = DefaultPipeline.user_model_inference,
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
        user_model_inference: UserModelInference
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
        self.user_model_inference = user_model_inference
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
    ) -> tuple[pd.DataFrame, VotingRights, list[UserModel], GlobalModel]:
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
        privacy: DataFrame with columns
            * `user_id`
            * `entity_id`
            * `is_public`
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
    
        logger.info(f"Pipeline 3. Computing user models with {self.user_models}")
        user_models = dict()
        for user, _ in users.iterrows():
            logger.info(f"    Pipeline 3.{user}. Computing user {user}'s model")
            user_models[user] = self.user_model_inference(judgments[user], entities)
        
        logger.info(f"Pipeline 4. Collaborative score scaling with {self.scaling}")
        user_models = self.scaling(user_models, users, privacy, entities)
        
        logger.info(f"Pipeline 5. Score aggregation with {self.aggregation}")
        global_model = self.aggregation(voting_rights, user_models, entities)
                
        logger.info(f"Pipeline 6. Post-processing scores {self.post_process}")
        user_models, global_model = self.post_process(user_models, global_model, entities)
        
        return trusts, voting_rights, user_models, global_model
