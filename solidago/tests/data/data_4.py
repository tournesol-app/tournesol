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

from solidago.generative_model import (NormalUserModel, ErdosRenyiVouchModel, NormalEntityModel,
    SimpleEngagementModel, KnaryGBT, GenerativeModel)


users, vouches, entities, privacy, judgments = GenerativeModel(
    user_model=NormalUserModel(
        p_trustworthy=0.8,
        p_pretrusted=0.8,
        zipf_vouch=1.2,
        zipf_compare=1.5,
        poisson_compare=10,
        n_comparisons_per_entity=4.0,
        svd_mean=np.array([3, 0, 0]),
        multiplicator_std_dev=0.2,
        engagement_bias_std_dev=1,
    ),
    vouch_model=ErdosRenyiVouchModel(),
    entity_model=NormalEntityModel(svd_dimension=3),
    engagement_model=SimpleEngagementModel(
        p_per_criterion={"0": 1.0}, 
        p_private=0.2
    ),
    comparison_model=KnaryGBT(21, 10)
)(10, 20, 0)

users = users.assign(trust_score=[
    0.012119914964822752, 0.8240785104076367, 0.8751253592623884, 0.8716451161435291,
    0.08168738970101802, 0.04447220842234952, 0.8446408787208469, 0.0, 0.0,
    0.8072849440069452
])
entities = entities.assign(cumulative_trust=[3.022399393325556,
    1.2599010684794012,
    0.9161173245658787,
    1.7401958349735152,
    1.7401958349735152,
    1.7300796457271632,
    1.6957236265511657,
    0.5397460519839573,
    2.584836713694362,
    1.3092077957747232,
    1.7401958349735152,
    1.7462557924559268,
    1.2599010684794012,
    1.328156579769697,
    3.060042732717755,
    2.6274411092007264,
    2.1611340705874205,
    0.9161173245658787,
    2.57472052444801,
    2.559600693945283
])
entities = entities.assign(min_voting_right=[0.968116283416748,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    0.7676520347595215,
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    0.6750273704528809,
    0.9780373573303223,
    0.7575688362121582,
    1.0,
    0.6548075675964355,
    0.9631123542785645
])
entities = entities.assign(overtrust=[2.302240165466558,
    0.2400989315205988,
    1.0838826754341213,
    1.2598041650264848,
    1.2598041650264848,
    1.7699203542728368,
    0.3042763734488343,
    1.4602539480160428,
    2.258483895856215,
    0.19079220422527676,
    1.2598041650264848,
    1.7537442075440732,
    0.2400989315205988,
    1.671843420230303,
    2.3060036731979108,
    2.262745677450885,
    2.2161143852493024,
    1.0838826754341213,
    2.257470467411527,
    2.255961077447539
])

pipeline = Pipeline(
    trust_propagation=LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=1.0,
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
            lipschitz=1,
            min_activity=0.1,
            n_scalers_max=20,
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
 0: {1: 0.968116283416748,
  2: 0.484058141708374,
  3: 0.968116283416748,
  5: 0.968116283416748,
  6: 0.968116283416748,
  8: 0.968116283416748},
 1: {1: 1.0, 3: 0.5},
 2: {3: 1.0, 5: 1.0},
 3: {1: 1.0, 3: 1.0, 5: 1.0},
 4: {1: 1.0, 3: 1.0, 5: 1.0},
 5: {0: 1.0, 1: 1.0, 3: 1.0, 5: 0.5},
 6: {1: 1.0, 3: 1.0},
 7: {3: 0.5, 4: 1.0, 5: 0.5},
 8: {1: 0.8240785104076367,
  3: 0.8716451161435291,
  5: 0.7676520347595215,
  6: 0.8446408787208469,
  7: 0.7676520347595215,
  8: 0.7676520347595215},
 9: {2: 0.5, 3: 1.0},
 10: {1: 1.0, 3: 1.0, 5: 1.0},
 11: {0: 0.5, 1: 1.0, 3: 1.0, 5: 1.0},
 12: {1: 1.0, 3: 0.5},
 13: {1: 0.5, 3: 1.0, 5: 1.0, 7: 0.5},
 14: {0: 0.6750273704528809,
  1: 0.41203925520381834,
  2: 0.8751253592623884,
  3: 0.8716451161435291,
  5: 0.6750273704528809,
  6: 0.8446408787208469,
  7: 0.6750273704528809,
  8: 0.33751368522644043},
 15: {0: 0.9780373573303223,
  1: 0.9780373573303223,
  2: 0.9780373573303223,
  3: 0.9780373573303223,
  5: 0.9780373573303223},
 16: {0: 0.7575688362121582,
  1: 0.8240785104076367,
  3: 0.43582255807176457,
  5: 0.7575688362121582,
  6: 0.8446408787208469,
  7: 0.7575688362121582},
 17: {3: 1.0, 5: 1.0},
 18: {0: 0.6548075675964355,
  1: 0.8240785104076367,
  3: 0.8716451161435291,
  5: 0.3274037837982178,
  6: 0.8446408787208469,
  7: 0.6548075675964355,
  8: 0.6548075675964355},
 19: {0: 0.9631123542785645,
  1: 0.9631123542785645,
  3: 0.9631123542785645,
  5: 0.9631123542785645,
  9: 0.9631123542785645}
})

learned_models = {
    0: DirectScoringModel({
        5: (-9.420934238935976, 0.09676241906089508, 0.09676241906089508),
        11: (0.9211990838673403, 0.035824621594679404, 0.035824621594679404),
        14: (6.801739267024673, 0.06822005349533646, 0.06822005349533646),
        15: (-5.21347603158661, 0.3534178539939361, 0.3534178539939361),
        16: (13.759503793189817, 0.055780025853559304, 0.055780025853559304),
        18: (-4.820897649644785, 0.397969733908756, 0.397969733908756),
        19: (-2.0269833093628473, 0.05553992889149402, 0.05553992889149402)
    }),
    1: DirectScoringModel({
        0: (2.655898210241207, 0.04417853826705255, 0.04417853826705255),
        3: (-1.904799240237743, 0.08974055805440168, 0.08974055805440168),
        4: (-8.310040298682503, 0.36538576993194344, 0.36538576993194344),
        5: (-1.7978985942549464, 0.2952358453536067, 0.2952358453536067),
        6: (-2.6048540199424366, 0.06947959277645349, 0.06947959277645349),
        8: (-3.828905825284274, 0.10269108836746632, 0.10269108836746632),
        10: (6.41803850384303, 0.04712732301053353, 0.04712732301053353),
        11: (8.631057063741078, 0.036043648922035175, 0.036043648922035175),
        12: (-8.800887146078413, 0.370588823669068, 0.370588823669068),
        13: (-9.170700719581468, 0.055361448368224334, 0.055361448368224334),
        14: (10.762862060050589, 0.09286184726138547, 0.09286184726138547),
        15: (-2.900447262557559, 0.2860415554558964, 0.2860415554558964),
        18: (3.8140429494822854, 0.16425374845300442, 0.16425374845300442),
        19: (7.0368151819609555, 0.19078050043235617, 0.19078050043235617)
    }),
    2: DirectScoringModel({
        0: (2.153162093259559, 0.16347271572937064, 0.16347271572937064),
        9: (-3.043543646005555, 0.28796291618741054, 0.28796291618741054),
        14: (5.50021503492929, 0.12818986267609864, 0.12818986267609864),
        15: (-4.609673507189205, 0.26900012571335874, 0.26900012571335874)
    }),
    3: DirectScoringModel({
        0: (4.949747345740672, 0.030612235321621762, 0.030612235321621762),
        17: (-3.072787895035313, 0.0468672480593411, 0.0468672480593411),
        1: (-4.949747346470931, 0.030612235321621762, 0.030612235321621762),
        14: (3.0727781165359365, 0.0468672480593411, 0.0468672480593411)
    }),
    4: DirectScoringModel({}),
    5: DirectScoringModel({
        0: (6.2343955953772285, 0.028761337145358605, 0.028761337145358605),
        2: (-1.3088063560486793, 0.036463173429796186, 0.036463173429796186),
        3: (4.870512417745178, 0.04406231478507909, 0.04406231478507909),
        4: (-7.099203123549771, 0.10733557712730728, 0.10733557712730728),
        5: (-0.18899419015175895, 0.02965163331350201, 0.02965163331350201),
        7: (-2.11471767093277, 0.04089929596649333, 0.04089929596649333),
        8: (-1.28404397332361, 0.1016286687939318, 0.1016286687939318),
        10: (6.583195007001783, 0.04804964875424704, 0.04804964875424704),
        11: (-3.4927187885048223, 0.33142433149022765, 0.33142433149022765),
        13: (-12.910198128849618, 0.03915309666002812, 0.03915309666002812),
        14: (2.6421518095472956, 0.08372349121022007, 0.08372349121022007),
        15: (-2.706975618823674, 0.3575618643232076, 0.3575618643232076),
        16: (11.256785210910582, 0.08751845375064934, 0.08751845375064934),
        17: (-10.590168964362485, 0.1277222914817508, 0.1277222914817508),
        18: (5.472009234748634, 0.06907792553411833, 0.06907792553411833),
        19: (4.636619017757722, 0.06591061036313917, 0.06591061036313917)
    }),
    6: DirectScoringModel({
        0: (-4.805632980395273, 0.3567340556781422, 0.3567340556781422),
        8: (-3.583442303463964, 0.412186995863811, 0.412186995863811),
        14: (7.5471236206855865, 0.0754965878075606, 0.0754965878075606),
        16: (1.0998327149371991, 0.35730836206349026, 0.35730836206349026),
        18: (-0.2575863492912141, 0.4089025225769248, 0.4089025225769248)
    }),
    7: DirectScoringModel({
        8: (0.7809377432118355, 0.22869007346993275, 0.22869007346993275),
        13: (10.633141975539049, 0.036697192672337266, 0.036697192672337266),
        14: (-8.228210713559719, 0.0820784995386319, 0.0820784995386319),
        16: (-2.1951831622636084, 0.3089966595024074, 0.3089966595024074),
        18: (-0.9904596973612348, 0.4979187829175371, 0.4979187829175371)
    }),
    8: DirectScoringModel({
        0: (3.948737726618275, 0.5877422935837447, 0.5877422935837447),
        8: (4.057965177049471, 0.576176116167437, 0.576176116167437),
        18: (2.506866737917168, 0.4748393316900625, 0.4748393316900625),
        14: (-10.513902238600377, 0.035796751959377975, 0.035796751959377975)
    }),
    9: DirectScoringModel({})
}

mehestan_scaled_models = {
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=0.10229987459532783,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8188964762439659,
        translation_right_uncertainty=0.8188964762439659,
    ),
    1: ScaledScoringModel(
        base_model=learned_models[1],
        multiplicator=1,
        translation=-0.15674047075920122,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8292836717603316,
        translation_right_uncertainty=0.8292836717603316,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=0.005882972178044258,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8816289783285892,
        translation_right_uncertainty=0.8816289783285892,
    ),
    3: ScaledScoringModel(
        base_model=learned_models[3],
        multiplicator=1,
        translation=-0.021224317176894335,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8096977551735333,
        translation_right_uncertainty=0.8096977551735333,
    ),
    5: ScaledScoringModel(
        base_model=learned_models[5],
        multiplicator=1,
        translation=-0.11699320071265393,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8185345094924429,
        translation_right_uncertainty=0.8185345094924429,
    ),
    6: ScaledScoringModel(
        base_model=learned_models[6],
        multiplicator=1,
        translation=0.11996250794687094,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.9815930147319589,
        translation_right_uncertainty=0.9815930147319589,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=0.0,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=1,
        translation_right_uncertainty=1,
    ),
    7: ScaledScoringModel(
        base_model=learned_models[7],
        multiplicator=1,
        translation=0.1025832119168861,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.9245814577721028,
        translation_right_uncertainty=0.9245814577721028,
    ),
    8: ScaledScoringModel(
        base_model=learned_models[8],
        multiplicator=1,
        translation=0.04847828040046153,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8990119261103918,
        translation_right_uncertainty=0.8990119261103918,
    ),
    9: ScaledScoringModel(
        base_model=learned_models[9],
        multiplicator=1,
        translation=0.0,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=1,
        translation_right_uncertainty=1,
    ),
}

zero_shifted_models = {
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=2.299762284216851,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8188964762439659,
        translation_right_uncertainty=0.8188964762439659,
    ),
    1: ScaledScoringModel(
        base_model=learned_models[1],
        multiplicator=1,
        translation=2.040721938862322,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8292836717603316,
        translation_right_uncertainty=0.8292836717603316,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=2.2033453817995676,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8816289783285892,
        translation_right_uncertainty=0.8816289783285892,
    ),
    3: ScaledScoringModel(
        base_model=learned_models[3],
        multiplicator=1,
        translation=2.176238092444629,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8096977551735333,
        translation_right_uncertainty=0.8096977551735333,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=2.197462409621523,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
    5: ScaledScoringModel(
        base_model=learned_models[5],
        multiplicator=1,
        translation=2.080469208908869,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8185345094924429,
        translation_right_uncertainty=0.8185345094924429,
    ),
    6: ScaledScoringModel(
        base_model=learned_models[6],
        multiplicator=1,
        translation=2.317424917568394,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.9815930147319589,
        translation_right_uncertainty=0.9815930147319589,
    ),
    7: ScaledScoringModel(
        base_model=learned_models[7],
        multiplicator=1,
        translation=2.197462409621523,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
    8: ScaledScoringModel(
        base_model=learned_models[8],
        multiplicator=1,
        translation=2.197462409621523,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
    9: ScaledScoringModel(
        base_model=learned_models[9],
        multiplicator=1,
        translation=2.197462409621523,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
}

standardized_models = {
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=0.23221562126287415,
        translation=0.5340407275863426,
        multiplicator_left_uncertainty=0.23221562126287415,
        multiplicator_right_uncertainty=0.23221562126287415,
        translation_left_uncertainty=0.190160553980971,
        translation_right_uncertainty=0.190160553980971,
    ),
    1: ScaledScoringModel(
        base_model=learned_models[1],
        multiplicator=0.23221562126287415,
        translation=0.4738875128576912,
        multiplicator_left_uncertainty=0.23221562126287415,
        multiplicator_right_uncertainty=0.23221562126287415,
        translation_left_uncertainty=0.1925726230409828,
        translation_right_uncertainty=0.1925726230409828,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=0.23221562126287415,
        translation=0.5116512166912712,
        multiplicator_left_uncertainty=0.23221562126287415,
        multiplicator_right_uncertainty=0.23221562126287415,
        translation_left_uncertainty=0.20472802092592635,
        translation_right_uncertainty=0.20472802092592635,
    ),
    3: ScaledScoringModel(
        base_model=learned_models[3],
        multiplicator=0.23221562126287415,
        translation=0.5053564806529617,
        multiplicator_left_uncertainty=0.23221562126287415,
        multiplicator_right_uncertainty=0.23221562126287415,
        translation_left_uncertainty=0.1880244672527766,
        translation_right_uncertainty=0.1880244672527766,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=0.23221562126287415,
        translation=0.5102850986520744,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
    5: ScaledScoringModel(
        base_model=learned_models[5],
        multiplicator=0.23221562126287415,
        translation=0.4831174498650534,
        multiplicator_left_uncertainty=0.23221562126287415,
        multiplicator_right_uncertainty=0.23221562126287415,
        translation_left_uncertainty=0.19007649964688958,
        translation_right_uncertainty=0.19007649964688958,
    ),
    6: ScaledScoringModel(
        base_model=learned_models[6],
        multiplicator=0.23221562126287415,
        translation=0.5381422669632095,
        multiplicator_left_uncertainty=0.23221562126287415,
        multiplicator_right_uncertainty=0.23221562126287415,
        translation_left_uncertainty=0.22794123174327943,
        translation_right_uncertainty=0.22794123174327943,
    ),
    7: ScaledScoringModel(
        base_model=learned_models[7],
        multiplicator=0.23221562126287415,
        translation=0.5102850986520744,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
    8: ScaledScoringModel(
        base_model=learned_models[8],
        multiplicator=0.23221562126287415,
        translation=0.5102850986520744,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
    9: ScaledScoringModel(
        base_model=learned_models[9],
        multiplicator=0.23221562126287415,
        translation=0.5102850986520744,
        multiplicator_left_uncertainty=0.0,
        multiplicator_right_uncertainty=0.0,
        translation_left_uncertainty=0.0,
        translation_right_uncertainty=0.0,
    ),
}

global_model = DirectScoringModel({
    0: (0.28480723454784973, 1.0463379238646644, 1.0463379238646644),
    1: (-0.02110129188815794, 0.9753803535846106, 0.9753803535846106),
    2: (0.02832967888862792, 0.9159895643945366, 0.9159895643945366),
    3: (0.06995952128096458, 0.9415894340637591, 0.9415894340637591),
    4: (-0.10372757374643692, 1.026693497135972, 1.026693497135972),
    5: (-0.005096690720645181, 0.9145679054728402, 0.9145679054728402),
    6: (-0.014451270153932947, 0.9010855649589123, 0.9010855649589123),
    7: (-0.0005345264252657221, 0.9499993098300769, 0.9499993098300769),
    8: (0.10001897979212003, 0.8296789218880134, 0.8296789218880134),
    9: (-0.00994388913240475, 0.9514005356313656, 0.9514005356313656),
    10: (0.14691444535061043, 1.0815324223598957, 1.0815324223598957),
    11: (0.07891312470196944, 0.9476149337046607, 0.9476149337046607),
    12: (-0.05604618904777661, 1.030417375405963, 1.030417375405963),
    13: (-0.0398710892388843, 1.113063945078853, 1.113063945078853),
    14: (0.21698410095722284, 1.1685325529766428, 1.1685325529766428),
    15: (-0.0903071697137848, 0.7340478815514363, 0.7340478815514363),
    16: (0.115081430989919, 0.979525080806357, 0.979525080806357),
    17: (-0.07314275080275766, 0.9462740407389584, 0.9462740407389584),
    18: (0.19689609332528954, 0.8902968209723224, 0.8902968209723224),
    19: (0.13269684798231798, 0.9819114242856011, 0.9819114242856011),
})

display_models, display_global_model = pipeline.post_process(
    standardized_models, global_model, entities)
