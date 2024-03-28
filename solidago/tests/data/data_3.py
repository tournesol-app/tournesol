import pandas as pd
import numpy as np

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.scoring_model import DirectScoringModel, ScaledScoringModel

from solidago.trust_propagation import LipschiTrust
from solidago.voting_rights import VotingRights, AffineOvertrust
from solidago.preference_learning import UniformGBT
from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import StandardizedQrMedian
from solidago.post_process import Squash
from solidago.pipeline import Pipeline


users = pd.DataFrame(dict(
    is_pretrusted=(np.arange(5) % 3 == 0),
    trust_score=[0.8, 0.0, 0.0, 0.8, 0.21333333333333335],
    svd0=[1, 2, 5, 2, 1],
    svd1=[7, 2, 0, 1, 9]
))
users.index.name = "user_id"

vouches = pd.DataFrame(dict(
    voucher=[0, 1, 2, 3],
    vouchee=[4, 4, 4, 4],
    vouch=[1, 1, 1, 1]
))

entities = pd.DataFrame(dict(
    cumulative_trust=[1.0133333333333334,
        0.6133333333333334,
        1.4133333333333336,
        1.0133333333333334,
        0.8
    ],
    min_voting_right=[0.8899044990539551, 0.8915553092956543, 1.0, 1.0, 1.0],
    overtrust=[2.101332413355509,
        2.0613325945536296,
        1.5866666666666664,
        1.4866666666666666,
        1.2
    ],
    svd0=[-1, 2, -1, 0, 0],
    svd1=[0, 0, 6, 4, 2]
))
entities.index.name = "entity_id"

privacy = PrivacySettings({
    0: { 0: True,  1: True, 2: False, 3: True, 4: False },
    1: { 1: True, 2: False, 3: True, 4: False },
    2: { 0: False,  1: True, 3: True, 4: False },
    3: { 0: True,  1: True, 3: True, 4: False },
    4: { 0: True,  1: True, 2: True, 3: True }
})

judgments = DataFrameJudgments(pd.DataFrame(dict(
    # The judgements contain a pair of entities (2, 3) compared twice by user 1
    # The learned models assume than only the last one is considered in the learning process.
    user_id= [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4],
    entity_a=[0, 2, 4, 0, 1, 4, 3, 4, 0, 2, 1, 0, 4, 0, 0, 0, 0, 2, 4, 0, 1, 2],
    entity_b=[2, 3, 3, 2, 2, 3, 2, 1, 4, 3, 0, 4, 1, 1, 2, 3, 4, 3, 3, 1, 2, 3],
    comparison=    [-5,3,-4,-3,-3, 2, 4,-4, 3, 2, 1, 3, 4, 1, 2, 1, 2, 0,-1, 2,-1,-2],
    comparison_max=[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
)))

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
    preference_learning=UniformGBT(
        prior_std_dev=7,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
    ),
    scaling=ScalingCompose(
        Mehestan(
            lipschitz=10,
            min_activity=0.1,
            n_scalers_max=100,
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
    aggregation=StandardizedQrMedian(
        dev_quantile=0.9,
        lipschitz=0.1,
        error=1e-5
    ),
    post_process=Squash(
        score_max=100
    )
)

voting_rights = VotingRights({
    0: {
        0: 0.44495224952697754,
        1: 0.44495224952697754,
        2: 0.8899044990539551,
        3: 0.44495224952697754,
        4: 0.8899044990539551
    },
    1: {
        1: 0.44577765464782715,
        2: 0.8915553092956543,
        3: 0.44577765464782715,
        4: 0.8915553092956543
    },
    2: {0: 1.0, 1: 0.5, 3: 0.5, 4: 1.0},
    3: {0: 0.5, 1: 0.5, 3: 0.5, 4: 1.0},
    4: {0: 0.5, 1: 0.5, 2: 0.5, 3: 0.5}
})

learned_models = {
    0: DirectScoringModel({
        0: (5.033398104293532, 0.03096002542681708, 0.03096002542681708),
        2: (-4.70158398961812, 0.16736063832963174, 0.16736063832963174),
        3: (-2.2520973379065916, 0.21329795423450776, 0.21329795423450776),
        4: (1.920367641692402, 0.07689734133169311, 0.07689734133169311)
    }),
    1: DirectScoringModel({
        0: (-0.2647961020419981, 0.4346751126408668, 0.4346751126408668),
        1: (-0.723484071079214, 0.4387030807322584, 0.4387030807322584),
        2: (-1.9388463288575928, 0.5587891835427051, 0.5587891835427051),
        3: (1.5444643844051669, 0.4306522267140735, 0.4306522267140735),
        4: (1.383154679686365, 0.7248330732791874, 0.7248330732791874)
    }),
    2: DirectScoringModel({
        0: (-0.41403365335425246, 0.6232992917299677, 0.6232992917299677),
        1: (0.6217382466724807, 0.5848617488561728, 0.5848617488561728),
        4: (-0.2073399097731925, 0.6429793786107434, 0.6429793786107434)
    }),
    3: DirectScoringModel({
        0: (-0.7616735994053457, 1.136102459884623, 1.136102459884623),
        1: (-0.1376152832458718, 0.32929993602267005, 0.32929993602267005),
        2: (0.26367367798854036, 0.6238313087499935, 0.6238313087499935),
        3: (0.03904465536134892, 0.958527480363601, 0.958527480363601),
        4: (0.5972697855709417, 0.5727475480020277, 0.5727475480020277)
    }),
    4: DirectScoringModel({
        0: (-0.374212225919361, 0.2649557275176049, 0.2649557275176049),
        1: (0.9304055634303148, 0.5771139502767695, 0.5771139502767695),
        2: (0.351959458123829, 0.5817762983596343, 0.5817762983596343),
        3: (-0.9084921677179439, 0.2696180756004697, 0.2696180756004697)
    })
}

mehestan_scaled_models = {
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=0.12889407714037499,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.9130213360845642,
        translation_right_uncertainty=0.9130213360845642,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=-0.1590548275385016,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.3830967247276593,
        translation_right_uncertainty=0.3830967247276593,
    ),
    1: ScaledScoringModel(
        base_model=learned_models[1],
        multiplicator=1,
        translation=-0.3639000734994202,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.7165751578351619,
        translation_right_uncertainty=0.7165751578351619,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=0.2801001117519021,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.6434822153922294,
        translation_right_uncertainty=0.6434822153922294,
    ),
    3: ScaledScoringModel(
        base_model=learned_models[3],
        multiplicator=1,
        translation=-0.3029613509557312,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.512473835218859,
        translation_right_uncertainty=0.512473835218859,
    ),
}

zero_shifted_models = {
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=0.12889407714037499,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.9130213360845642,
        translation_right_uncertainty=0.9130213360845642,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=-0.1590548275385016,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.3830967247276593,
        translation_right_uncertainty=0.3830967247276593,
    ),
    1: ScaledScoringModel(
        base_model=learned_models[1],
        multiplicator=1,
        translation=-0.3639000734994202,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.7165751578351619,
        translation_right_uncertainty=0.7165751578351619,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=0.2801001117519021,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.6434822153922294,
        translation_right_uncertainty=0.6434822153922294,
    ),
    3: ScaledScoringModel(
        base_model=learned_models[3],
        multiplicator=1,
        translation=-0.3029613509557312,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.512473835218859,
        translation_right_uncertainty=0.512473835218859,
    ),
}


standardized_models = {
    0: DirectScoringModel({
        0: (3.264569524098553, 3.760441873550323, 3.799599345433532),
        2: (-2.8917123647350933, 3.7622803267181295, 3.5506067444325042),
        3: (-1.3426873983407066, 2.2713557375403965, 2.0015817780381173),
        4: (1.295927684655978, 1.791800034107748, 1.8890578832076104)
    }),
    4: DirectScoringModel({
        0: (-0.3372314680647955, 0.8140222132914514, 0.4789127840343592),
        1: (0.4877926347988997, 0.8306425496751277, 1.5605619528354313),
        2: (0.12199049490674634, 0.7555070463816187, 1.2006566351017756),
        3: (-0.6751034741487916, 1.1577910415339454, 0.8167847901183554)
    }),
    1: DirectScoringModel({
        0: (-0.39757966082805796, 1.1703733042801017, 0.8354657653634321),
        1: (-0.6876482412495606, 1.4655363587891002, 0.9106755887468789),
        2: (-1.456228253390763, 2.3859982938143567, 1.679255600888081),
        3: (0.7465742222964976, 1.4298533525332622, 1.9745316021961616),
        4: (0.6445639664918632, 1.3278430967286279, 2.244593980995183)
    }),
    2: DirectScoringModel({
        0: (-0.08469790992112539, 1.457093391141368, 0.9334339006721408),
        1: (0.5703113882557368, 0.8001097219133108, 1.5398283484543214),
        4: (0.0460126489549014, 1.3512737177885028, 1.0890353450713293)
    }),
    3: DirectScoringModel({
        0: (-0.6732619330883267, 2.242669227345483, 1.2793233598365013),
        1: (-0.2786151969889006, 0.8275986799638642, 0.6535462846537343),
        2: (-0.02484503692036591, 0.9463444912906003, 1.2798324161175398),
        3: (-0.16689764373214913, 1.5117125104348736, 1.5610952216382468),
        4: (0.18611700240165277, 0.7017880965790018, 1.4261849824949917)
    })
}

global_model = DirectScoringModel({
    0: (-0.05484195288581686, 0.8103578532927556, 0.8103578532927556),
    1: (0.04347769005366959, 0.904287730402594, 0.904287730402594),
    2: (-0.06752185688076714, 0.9837973012434301, 0.9837973012434301),
    3: (-0.0652762411451413, 0.9164216582568455, 0.9164216582568455),
    4: (0.05719054409869791, 0.9300590263865601, 0.9300590263865601),
})

display_models, display_global_model = pipeline.post_process(
    standardized_models, global_model, entities)
