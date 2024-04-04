import logging
from threading import Thread

from solidago.pipeline.inputs import TournesolInputFromPublicDataset

from solidago.trust_propagation import LipschiTrust
from solidago.voting_rights import AffineOvertrust
from solidago.preference_learning import LBFGSUniformGBT
from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import StandardizedQrQuantile
from solidago.post_process import Squash
from solidago.pipeline import Pipeline


logger = logging.getLogger(__name__)

info_loggers = [
    __name__, 
    "solidago.pipeline.pipeline", 
    "solidago.scaling.mehestan",
    "solidago.preference_learning.base"
]
for module in info_loggers:
    info_logger = logging.getLogger(module)
    info_logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    info_logger.addHandler(ch)


pipeline = Pipeline(
    trust_propagation=LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    ),
    voting_rights=AffineOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    ),
    preference_learning=LBFGSUniformGBT(
        prior_std_dev=7,
        comparison_max=10,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
        n_steps=2,
    ),
    scaling=ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_activity=10,
            n_scalers_max=500,
            privacy_penalty=0.5,
            p_norm_for_multiplicative_resilience=4.0,
            error=1e-5
        ),
        QuantileZeroShift(
            zero_quantile=0.15,
            lipschitz=0.1,
            error=1e-5
        )
    ),
    aggregation=StandardizedQrQuantile(
        quantile=0.2,
        dev_quantile=0.9,
        lipschitz=0.1,
        error=1e-5
    ),
    post_process= Squash(
        score_max=100
    )
)

logger.info("Retrieve public dataset")
inputs = TournesolInputFromPublicDataset.download()

logger.info("Preprocessing data for the pipeline")
users, vouches, entities, privacy = inputs.get_pipeline_objects()

# criteria = set(inputs.comparisons["criteria"])
criteria = { "largely_recommended" }

user_outputs, voting_rights, user_models, global_model = dict(), dict(), dict(), dict()
def run_pipeline(criterion):
    logger.info(f"Running the pipeline for criterion `{criterion}`")
    judgments = inputs.get_judgments(criterion)
    output = pipeline(users, vouches, entities, privacy, judgments)
    user_outputs[criterion], voting_rights[criterion] = output[0], output[1]
    user_models[criterion], global_model[criterion] = output[2], output[3]

threads = [Thread(target=run_pipeline, args=(criterion,)) for criterion in criteria]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
    
logger.info(f"Successful pipeline run.")
