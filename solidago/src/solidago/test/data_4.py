import pandas as pd
import numpy as np

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.scoring_model import DirectScoringModel

from solidago.trust_propagation import LipschiTrust
from solidago.voting_rights import VotingRights, AffineOvertrust
from solidago.preference_learning import UniformGBT
from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import QuantileStandardizedQrMedian
from solidago.post_process import Squash
from solidago.pipeline import Pipeline


np.random.seed(0)

users = pd.DataFrame(dict(
    is_pretrusted=np.random.random(20) < 0.20,
    trust_score=[0.04478270804619478, 3.7355199183719185e-05, 0.03637379712287813,
        0.00214102869722107, 0.009943012913209853, 0.0001413345069935354,
        0.03476165169428667, 0.0023141842257231823, 0.0003555730318881166,
        0.017198996028511854, 7.978870514876874e-05, 0.040830925916064895, 
        0.0, 0.002020051872783562, 0.8449119837046595, 0.8000921460641155, 
        0.8028373541319094, 0.0042177586804884246, 0.0015930263323911784, 
        0.000788923880714716
    ],
    svd0=np.random.normal(1, 1, 20),
    svd1=np.random.normal(1, 1, 20),
    svd2=np.random.normal(1, 1, 20),
    svd3=np.random.normal(1, 1, 20),
    svd4=np.random.normal(1, 1, 20)
), index=2 * np.arange(20) + 3)
users.index.name = "user_id"

vouches = pd.DataFrame(dict(
    voucher=2 * np.random.randint(0, 20, 80) + 3,
    vouchee=2 * np.random.randint(0, 20, 80) + 3,
    vouch=np.random.random(80)
))
vouches["vouchee"] += 2 * (vouches["vouchee"] == vouches["voucher"])
vouches["vouchee"] = ((vouches["vouchee"] - 3) % 40) + 3

entities = pd.DataFrame(dict(
    cumulative_trust=[
        0.08553559052356141,
        0.4014186770659547,
        0.03853518350265523,
        0.0042177586804884246,
        0.005412205992533735,
        0.8001719347692643,
        0.003907210558114361,
        0.03855218101928292,
        0.8028373541319094,
        0.006710632612388861,
        1.6171700604948718,
        0.4848855022960264,
        0.8028373541319094,
        0.11232194776511781,
        0.04478270804619478,
        0.8029011218176137,
        0.0311709943916105,
        0.884782783181697,
        0.8861945915905022,
        0.000496907538881652,
        0.9343993563583508,
        0.9191969144076122,
        0.015895132433082992,
        0.8120266192690028,
        0.0001413345069935354,
        0.9221388301470671,
        0.01630180029091935,
        0.8204404310053316,
        0.11706265377596241,
        0.8050183373545026,
        0.08553559052356141,
        0.08983139264274811,
        0.002744386775776495,
        0.006545146794217083,
        0.9325456695397027,
        1.6520751189697378,
        0.019613509841652773,
        0.0480135513849564,
        0.002787473644436489,
        0.8520956327836043,
        0.0008076014803065756,
        1.615013541806456,
        0.04706507125040939,
        0.889774480456003,
        0.8945111695713086,
        0.8449119837046595,
        0.0023819502131058943,
        0.8824302777401405,
        0.8010597596510074,
        1.649769615314187
    ],
    voting_right=[
        0.6980299949645996,
        1.0,
        0.6807961463928223,
        1.0,
        0.8023810386657715,
        1.0,
        1.0,
        0.5106015205383301,
        1.0,
        0.5018458366394043,
        0.7253193855285645,
        0.844367504119873,
        1.0,
        0.424710750579834,
        1.0,
        0.6943659782409668,
        0.31296777725219727,
        0.7234749794006348,
        0.3042721748352051,
        1.0,
        0.7276425361633301,
        0.48137903213500977,
        0.504371166229248,
        1.0,
        1.0,
        0.723146915435791,
        0.6726441383361816,
        0.8292813301086426,
        0.4257540702819824,
        0.3791689872741699,
        0.523521900177002,
        0.6996045112609863,
        0.8012070655822754,
        0.4014401435852051,
        0.7269625663757324,
        0.8482851982116699,
        0.8086295127868652,
        0.5865187644958496,
        0.8012261390686035,
        0.5336165428161621,
        1.0,
        0.9441285133361816,
        0.5129427909851074,
        0.711280345916748,
        0.3970675468444824,
        1.0,
        1.0,
        0.6073603630065918,
        0.6936907768249512,
        0.5529541969299316
    ],
    overtrust=        [
        2.0085543943702375,
        0.09858132293404531,
        2.0038532556758115,
        1.4957822413195117,
        2.000540390671895,
        1.1998280652307356,
        1.9960927894418856,
        2.0038539011340375,
        0.19716264586809062,
        2.000672713945228,
        2.1617175962868465,
        2.0484892498559857,
        0.19716264586809062,
        2.0112318051340523,
        0.9552172919538052,
        2.080288958969402,
        2.003119557747672,
        2.0884795091521164,
        2.0886226159605927,
        1.9995030924611183,
        2.093440235836299,
        2.0919207139045914,
        2.0015895324839095,
        1.6879733807309973,
        0.9998586654930065,
        2.0922138998649658,
        2.0016306147176257,
        2.0820442243749175,
        2.0117076976339496,
        2.0805032387175473,
        2.0085520101844465,
        2.008982141140211,
        2.000273277179912,
        2.0006555711318086,
        2.093254013292154,
        2.1652082729827766,
        2.00196027212551,
        2.004802124350517,
        2.0002778740270726,
        2.0852078926129534,
        1.4991923985196935,
        2.1615005115382706,
        2.00470609269002,
        2.088978540998901,
        2.0894524841374604,
        1.1550880162953405,
        1.997618049786894,
        2.0882429764875905,
        2.080104716887962,
        2.1649766726015645
    ],        
    svd0=np.random.normal(0, 1, 50),
    svd1=np.random.normal(0, 1, 50),
    svd2=np.random.normal(0, 1, 50),
    svd3=np.random.normal(0, 1, 50),
    svd4=np.random.normal(0, 1, 50)
), index=3*np.arange(50) + 5)
entities.index.name = "entity_id"

privacy = PrivacySettings()
for _ in range(20 * 10):
    user = 2 * np.random.randint(20) + 3
    entity = 3 * np.random.randint(50) + 5
    privacy[user, entity] = (np.random.random() < 0.1)

judgments = list()
for user in users.index:
    user_entities = list(privacy.entities(user))
    for e_index, e in enumerate(user_entities):
        for f in user_entities[e_index + 1:]:
            if np.random.random() <= 0.2:
                continue
            comparison_max = np.random.random() * 10
            comparison = (2 * np.random.random() - 1) * comparison_max
            judgments.append((user, e, f, comparison, comparison_max))
judgments = list(zip(*judgments))
judgments = DataFrameJudgments(pd.DataFrame(dict(
    user_id=judgments[0],
    entity_a=judgments[1],
    entity_b=judgments[2],
    comparison=judgments[3],
    comparison_max=judgments[4]
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
            lipschitz=1,
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
    aggregation=QuantileStandardizedQrMedian(
        dev_quantile=0.9,
        lipschitz=0.1,
        error=1e-5
    ),
    post_process=Squash(
        score_max=100
    )
)

voting_rights = VotingRights({
    128: {
        11: 0.9441285133361816,
        9: 0.9441285133361816,
        35: 0.9441285133361816,
        33: 0.9441285133361816
    },
    131: {
        27: 0.5129427909851074,
        9: 0.5129427909851074,
        3: 0.5129427909851074,
        13: 0.5129427909851074
    },
    5: {25: 0.6980299949645996, 11: 0.6980299949645996, 15: 0.6980299949645996},
    134: {
        3: 0.711280345916748,
        27: 0.711280345916748,
        31: 0.8449119837046595,
        23: 0.711280345916748
    },
    8: {35: 0.5},
    137: {
        33: 0.8000921460641155,
        3: 0.3970675468444824,
        37: 0.3970675468444824,
        5: 0.3970675468444824,
        15: 0.3970675468444824,
        21: 0.1985337734222412,
        29: 0.3970675468444824
    },
    11: {13: 0.6807961463928223, 29: 0.6807961463928223, 7: 0.6807961463928223},
    140: {27: 1.0, 31: 1.0},
    14: {27: 0.5, 37: 1.0},
    143: {41: 1.0, 39: 1.0},
    17: {17: 0.40119051933288574, 37: 0.8023810386657715, 5: 0.8023810386657715},
    146: {
        7: 0.6073603630065918,
        41: 0.6073603630065918,
        19: 0.6073603630065918,
        27: 0.3036801815032959,
        31: 0.8449119837046595
    },
    20: {33: 1.0, 23: 1.0},
    149: {
        33: 0.8000921460641155,
        5: 0.6936907768249512,
        13: 0.6936907768249512,
        41: 0.6936907768249512
    },
    23: {17: 1.0, 39: 1.0},
    152: {
        33: 0.8000921460641155,
        3: 0.5529541969299316,
        35: 0.8028373541319094,
        5: 0.5529541969299316,
        27: 0.5529541969299316,
        29: 0.5529541969299316
    },
    26: {
        9: 0.5106015205383301,
        27: 0.5106015205383301,
        5: 0.5106015205383301,
        7: 0.5106015205383301
    },
    29: {35: 1.0},
    32: {
        17: 0.5018458366394043,
        5: 0.5018458366394043,
        13: 0.5018458366394043,
        37: 0.5018458366394043
    },
    35: {
        33: 0.8000921460641155,
        35: 0.8028373541319094,
        37: 0.7253193855285645,
        11: 0.7253193855285645,
        23: 0.7253193855285645
    },
    38: {
        25: 0.844367504119873,
        31: 0.42245599185232974,
        37: 0.844367504119873,
        15: 0.4221837520599365
    },
    41: {35: 1.0},
    44: {
        7: 0.424710750579834,
        15: 0.424710750579834,
        19: 0.424710750579834,
        25: 0.424710750579834,
        27: 0.424710750579834
    },
    47: {3: 1.0},
    50: {
        41: 0.6943659782409668,
        27: 0.6943659782409668,
        29: 0.6943659782409668,
        33: 0.8000921460641155
    },
    53: {
        5: 0.31296777725219727,
        39: 0.31296777725219727,
        9: 0.31296777725219727,
        11: 0.31296777725219727,
        19: 0.15648388862609863,
        21: 0.31296777725219727,
        23: 0.31296777725219727
    },
    56: {
        3: 0.7234749794006348,
        41: 0.7234749794006348,
        35: 0.8028373541319094,
        7: 0.7234749794006348
    },
    59: {
        5: 0.3042721748352051,
        39: 0.3042721748352051,
        9: 0.3042721748352051,
        15: 0.3042721748352051,
        17: 0.3042721748352051,
        19: 0.3042721748352051,
        23: 0.3042721748352051,
        31: 0.8449119837046595
    },
    62: {19: 1.0, 13: 1.0},
    65: {
        11: 0.7276425361633301,
        3: 0.7276425361633301,
        15: 0.7276425361633301,
        31: 0.8449119837046595
    },
    68: {
        3: 0.48137903213500977,
        5: 0.48137903213500977,
        9: 0.48137903213500977,
        11: 0.48137903213500977,
        15: 0.24068951606750488,
        31: 0.8449119837046595
    },
    71: {
        37: 0.504371166229248,
        11: 0.504371166229248,
        13: 0.504371166229248,
        39: 0.504371166229248
    },
    74: {11: 0.5, 35: 1.0, 37: 1.0},
    77: {13: 1.0},
    80: {
        7: 0.3615734577178955,
        21: 0.723146915435791,
        25: 0.723146915435791,
        29: 0.3615734577178955,
        31: 0.8449119837046595
    },
    83: {9: 0.6726441383361816, 11: 0.6726441383361816, 37: 0.6726441383361816},
    86: {
        33: 0.8292813301086426,
        29: 0.8292813301086426,
        13: 0.8292813301086426,
        7: 0.4146406650543213
    },
    89: {
        3: 0.4257540702819824,
        7: 0.4257540702819824,
        41: 0.4257540702819824,
        15: 0.4257540702819824,
        19: 0.4257540702819824
    },
    92: {
        33: 0.8000921460641155,
        37: 0.18958449363708496,
        39: 0.3791689872741699,
        41: 0.3791689872741699,
        19: 0.3791689872741699,
        23: 0.3791689872741699,
        27: 0.3791689872741699
    },
    95: {
        27: 0.523521900177002,
        25: 0.523521900177002,
        11: 0.523521900177002,
        15: 0.523521900177002
    },
    98: {25: 0.6996045112609863, 3: 0.6996045112609863, 37: 0.6996045112609863},
    101: {13: 0.8012070655822754, 29: 0.4006035327911377, 39: 0.8012070655822754},
    104: {
        39: 0.4014401435852051,
        9: 0.4014401435852051,
        13: 0.4014401435852051,
        17: 0.4014401435852051,
        19: 0.4014401435852051
    },
    107: {
        25: 0.7269625663757324,
        3: 0.7269625663757324,
        29: 0.7269625663757324,
        31: 0.8449119837046595
    },
    110: {
        35: 0.8482851982116699,
        5: 0.8482851982116699,
        37: 0.8482851982116699,
        13: 0.42414259910583496,
        31: 0.8482851982116699
    },
    113: {41: 0.4043147563934326, 21: 0.8086295127868652, 29: 0.8086295127868652},
    116: {
        9: 0.5865187644958496,
        3: 0.5865187644958496,
        29: 0.2932593822479248,
        23: 0.5865187644958496
    },
    119: {17: 0.40061306953430176, 5: 0.8012261390686035, 39: 0.8012261390686035},
    122: {
        3: 0.5336165428161621,
        35: 0.8028373541319094,
        13: 0.5336165428161621,
        17: 0.5336165428161621,
        29: 0.5336165428161621
    },
     125: {41: 1.0, 5: 0.5}
})

learned_models = {
    3: DirectScoringModel({
        65: (0.2952849875176714, 3.478593907191462, 3.478593907191462),
        98: (-0.8748470584166946, 2.820620278174437, 2.820620278174437),
        131: (-0.09189197409490461, 3.536787024365235, 3.536787024365235),
        68: (-0.394516636703687, 3.193382532842699, 3.193382532842699),
        56: (0.004499230176132831, 3.8747772877950464, 3.8747772877950464),
        134: (0.053837102882642256, 2.8875499009650305, 2.8875499009650305),
        137: (-0.34318713318315813, 3.1706530642840445, 3.1706530642840445),
        107: (0.2430954765516152, 3.522330938749759, 3.522330938749759),
        47: (0.5432273219352545, 2.5226785723909355, 2.5226785723909355),
        116: (-0.24741444199749582, 2.9029701212496466, 2.9029701212496466),
        152: (0.8705295528313921, 2.481201565785803, 2.481201565785803),
        89: (-0.19943416972429798, 3.513866034936558, 3.513866034936558),
        122: (0.14811024158978614, 2.8705558137143057, 2.8705558137143057)
    }),
    5: DirectScoringModel({
        32: (0.23496446998827744, 2.5718969418997233, 2.5718969418997233),
        68: (0.7350550446142297, 3.2195778181395074, 3.2195778181395074),
        137: (-0.39668823617621135, 3.1478663125438944, 3.1478663125438944),
        110: (0.5214295887712401, 3.3905027981401146, 3.3905027981401146),
        17: (-0.10796201374761466, 3.2492580081042317, 3.2492580081042317),
        149: (0.3907991571748741, 2.837139174971307, 2.837139174971307),
        53: (0.002098542277388952, 2.94312416538982, 2.94312416538982),
        119: (-0.23924035139628758, 3.544829370426455, 3.544829370426455),
        152: (-0.21882331076316536, 2.897787461793744, 2.897787461793744),
        26: (-0.5355080825655112, 2.7534448248987955, 2.7534448248987955),
        59: (-0.21252240627795274, 3.242473689634674, 3.242473689634674),
        125: (-0.18064726240132387, 2.2504830620837755, 2.2504830620837755)
    }),
    7: DirectScoringModel({
        11: (0.3107747134428202, 2.1697654197033485, 2.1697654197033485),
        44: (0.02626044184435185, 2.1927531117224848, 2.1927531117224848),
        80: (0.7120122602745705, 1.8611819171790855, 1.8611819171790855),
        146: (-0.016563594815803655, 2.1904533420253034, 2.1904533420253034),
        86: (-0.4128830063278632, 1.8161940073104221, 1.8161940073104221),
        56: (0.4858608440673082, 1.8373621608001514, 1.8373621608001514),
        89: (-1.3549953361482854, 1.1751254817483172, 1.1751254817483172),
        26: (0.25248069719003224, 1.9672457187674952, 1.9672457187674952)
    }),
    9: DirectScoringModel({
        128: (-1.546184873633308, 1.632749069843364, 1.632749069843364),
        131: (0.2477379972259765, 1.5572016341490946, 1.5572016341490946),
        68: (-0.7735831905446774, 1.799766863366012, 1.799766863366012),
        104: (0.7241635389878668, 1.7270967501658188, 1.7270967501658188),
        83: (2.2527854011473285, 0.7208620549354838, 0.7208620549354838),
        116: (0.728260712673303, 1.7886601976953513, 1.7886601976953513),
        53: (-0.5216214346092899, 1.8870975383014494, 1.8870975383014494),
        26: (-0.9238480040381511, 2.0510972479191274, 2.0510972479191274),
        59: (-0.18519301448233472, 1.1690910892588637, 1.1690910892588637)
    }),
    11: DirectScoringModel({
        128: (1.2849054973055372, 1.6524912320967842, 1.6524912320967842),
        65: (1.6930006466913217, 1.3352604747744024, 1.3352604747744024),
        35: (-0.3638701979827119, 2.196811428233684, 2.196811428233684),
        68: (-2.3225599644234176, 1.1951601329313335, 1.1951601329313335),
        5: (-1.218067260691771, 1.789837691548355, 1.789837691548355),
        71: (0.3495018678254126, 1.7825890717067394, 1.7825890717067394),
        74: (0.20086907953074867, 2.282459250165796, 2.282459250165796),
        83: (1.4274461895837973, 1.9774678249441315, 1.9774678249441315),
        53: (0.6180337470314192, 1.7820647067821476, 1.7820647067821476),
        95: (-1.6656528211798676, 1.3625929593975594, 1.3625929593975594)
    }),
    13: DirectScoringModel({
        32: (0.5336509841970819, 2.3822623691368214, 2.3822623691368214),
        131: (0.8523461388487433, 2.6689086573759147, 2.6689086573759147),
        101: (-0.1659050222956258, 2.784453750242977, 2.784453750242977),
        71: (-0.10251875444461787, 2.569067242451714, 2.569067242451714),
        104: (0.8180417840825764, 3.0002524432004267, 3.0002524432004267),
        11: (-2.4647020692975827, 1.1230786292504356, 1.1230786292504356),
        77: (-1.3347270518593612, 1.8840488788972427, 1.8840488788972427),
        110: (-0.7231388274688554, 1.7660180471552867, 1.7660180471552867),
        149: (0.6359572317172765, 2.3586818655743724, 2.3586818655743724),
        86: (0.4322679591931795, 2.219775779533221, 2.219775779533221),
        122: (0.2730010684204017, 2.4558319785788494, 2.4558319785788494),
        62: (1.2506463290487557, 2.1498062862455884, 2.1498062862455884)
    }),
    15: DirectScoringModel({
        65: (0.7864629261849472, 1.2325620251893181, 1.2325620251893181),
        68: (-0.16609265235626022, 2.4391824532774606, 2.4391824532774606),
        5: (-0.12463646463519094, 1.5762850311068703, 1.5762850311068703),
        38: (0.23007772696801948, 1.8750347142334065, 1.8750347142334065),
        137: (-0.9208813706884313, 1.492538886026671, 1.492538886026671),
        44: (0.9387114893828497, 1.6191554447553655, 1.6191554447553655),
        89: (0.4638350343779958, 1.831847915849014, 1.831847915849014),
        59: (-1.1549156956273243, 1.2695209266361567, 1.2695209266361567),
        95: (-0.04988828427602484, 2.124367137873475, 2.124367137873475)
    }),
    17: DirectScoringModel({
        32: (0.9506870904604948, 1.262743277566586, 1.262743277566586),
        104: (-1.5306249645757997, 0.8312893785154063, 0.8312893785154063),
        17: (0.8396630322597519, 1.1310555693949589, 1.1310555693949589),
        23: (0.2103802627245521, 1.4254810482953058, 1.4254810482953058),
        119: (-0.046561878914738175, 1.1863948807945355, 1.1863948807945355),
        122: (0.6447254135656273, 1.0290835713129625, 1.0290835713129625),
        59: (-1.0666561627392233, 1.418434697432154, 1.418434697432154)
    }),
    19: DirectScoringModel({
        104: (-0.0435848471514145, 1.534440926541558, 1.534440926541558),
        44: (-0.2868626483585518, 2.1094367460654873, 2.1094367460654873),
        146: (-1.0060281112772698, 1.6738625857010043, 1.6738625857010043),
        53: (-0.17456878805971732, 2.124215277784052, 2.124215277784052),
        89: (1.2846530345436609, 1.4611651761846614, 1.4611651761846614),
        59: (-0.722743169301343, 1.6664458630631036, 1.6664458630631036),
        92: (0.15356896744965448, 2.1158116788920776, 2.1158116788920776),
        62: (0.7983328060263452, 1.6062438231142615, 1.6062438231142615)
    }),
    21: DirectScoringModel({
        80: (0.5401933197643154, 0.9069732228739967, 0.9069732228739967),
        113: (-0.12145008010773944, 0.9619181798265426, 0.9619181798265426),
        137: (0.27663191618340877, 0.950801335783809, 0.950801335783809),
        53: (-0.6960837107680585, 0.8631953406641643, 0.8631953406641643)
    }),
    23: DirectScoringModel({
        35: (-0.4924055729542731, 1.1898280946247575, 1.1898280946247575),
        134: (-0.8466131773600214, 1.6149179730221161, 1.6149179730221161),
        116: (-0.857958783435607, 1.2965128909596564, 1.2965128909596564),
        53: (1.3532625965524647, 1.3045804934332916, 1.3045804934332916),
        20: (0.09219931377180243, 1.4347077549563063, 1.4347077549563063),
        59: (-0.3065182764972685, 1.4348695169640664, 1.4348695169640664),
        92: (1.0560263731133392, 1.2310003157513087, 1.2310003157513087)
    }),
    25: DirectScoringModel({
        98: (0.194395736645819, 1.5535221684814342, 1.5535221684814342),
        5: (0.9019705351714165, 1.6043651069935705, 1.6043651069935705),
        38: (-0.9346612949870752, 1.5844268176396992, 1.5844268176396992),
        107: (0.7871462330540572, 1.658049011897761, 1.658049011897761),
        44: (-0.7942295308649965, 1.374243477792411, 1.374243477792411),
        80: (-0.13327547695148384, 1.835881466061705, 1.835881466061705),
        95: (-0.019138349909395433, 1.8417604246471437, 1.8417604246471437)
    }),
    27: DirectScoringModel({
        131: (0.1503646545177213, 2.3458383028899, 2.3458383028899),
        134: (0.20633971321527225, 1.9835186079163571, 1.9835186079163571),
        140: (-1.2611792535480073, 1.7582051247646837, 1.7582051247646837),
        44: (-0.19077442900446945, 2.676654834122535, 2.676654834122535),
        14: (-0.6718081385224377, 2.429236081648392, 2.429236081648392),
        146: (2.263189308162473, 1.0784439557552972, 1.0784439557552972),
        50: (-0.7274634258164049, 2.2342411585661175, 2.2342411585661175),
        152: (-0.6960087503935498, 2.5955178374034653, 2.5955178374034653),
        26: (0.8948398182349178, 1.891340750758098, 1.891340750758098),
        92: (0.2576917109454228, 2.2584361141759843, 2.2584361141759843),
        95: (-0.22088631090865662, 2.619761290965081, 2.619761290965081)
    }),
    29: DirectScoringModel({
        101: (0.725428836446588, 2.4417164922021146, 2.4417164922021146),
        137: (-0.5323014388912353, 2.0341285797508544, 2.0341285797508544),
        11: (-0.7452853824186528, 2.1603029442631954, 2.1603029442631954),
        107: (-0.0823326489028951, 3.0967968578578526, 3.0967968578578526),
        80: (0.6693553876826619, 2.6113433640872676, 2.6113433640872676),
        113: (-0.05933900945787063, 2.5245508351569645, 2.5245508351569645),
        50: (-1.2719767631059402, 1.7211597921712767, 1.7211597921712767),
        116: (0.6741081059287382, 2.5709823284041455, 2.5709823284041455),
        86: (-0.178795884133199, 2.151019971315862, 2.151019971315862),
        152: (0.38239669513080926, 1.8539487942058648, 1.8539487942058648),
        122: (0.42316749619359617, 2.6948462908095236, 2.6948462908095236)
    }),
    31: DirectScoringModel({
        65: (-0.06466213450907149, 2.4703482823356704, 2.4703482823356704),
        68: (0.511430730946646, 2.3759437933101775, 2.3759437933101775),
        134: (0.5840001079216063, 2.3479783053193604, 2.3479783053193604),
        38: (-1.0416218100874348, 2.3276418196483823, 2.3276418196483823),
        107: (-0.4121296117569629, 2.1439266249327606, 2.1439266249327606),
        140: (-0.4037014244585956, 2.377954622223016, 2.377954622223016),
        110: (-0.7048325370667798, 2.254074201681441, 2.254074201681441),
        80: (1.0569152193684006, 2.0554257610020388, 2.0554257610020388),
        146: (-0.13866974812339083, 2.186651211238858, 2.186651211238858),
        59: (0.6173420818790011, 2.6068948696452607, 2.6068948696452607)
    }),
    33: DirectScoringModel({
        128: (0.2461596782160765, 2.4837130294553895, 2.4837130294553895),
        35: (-0.972663611154941, 2.1223781144091816, 2.1223781144091816),
        137: (-0.40269689725674507, 2.2077637349207904, 2.2077637349207904),
        50: (0.1372273994092978, 2.173145483811317, 2.173145483811317),
        20: (0.014696112914018898, 2.509965459362542, 2.509965459362542),
        149: (0.22597419252342243, 2.2048650173006044, 2.2048650173006044),
        86: (1.0523726190439904, 1.5326129283338077, 1.5326129283338077),
        152: (-0.7007600951731267, 2.0145203117794375, 2.0145203117794375),
        92: (0.39623515910736096, 1.8061808984021672, 1.8061808984021672)
    }),
    35: DirectScoringModel({
        128: (-0.5552311480806134, 2.3620214730273865, 2.3620214730273865),
        35: (-1.0593785690386015, 1.5807016216920318, 1.5807016216920318),
        56: (0.3331896411681696, 2.767424297451799, 2.767424297451799),
        8: (-0.032820297983547214, 2.8189727829621956, 2.8189727829621956),
        41: (0.11908111805209246, 1.9192052157393316, 1.9192052157393316),
        74: (-0.6013751419360993, 2.1776480131705123, 2.1776480131705123),
        110: (1.0274540139234924, 1.5821176228525524, 1.5821176228525524),
        152: (-0.04461179614893028, 1.9436544619241671, 1.9436544619241671),
        122: (0.6127939236022759, 2.1835435413051534, 2.1835435413051534),
        29: (0.2049661891583518, 2.507800582807089, 2.507800582807089)
    }),
    37: DirectScoringModel({
        32: (0.8858004497744586, 1.7466636854550632, 1.7466636854550632),
        98: (-0.674147125170653, 2.1959968668259955, 2.1959968668259955),
        35: (-0.09685168715663098, 2.7553928361669247, 2.7553928361669247),
        38: (-0.3022949527077189, 2.3246896638081003, 2.3246896638081003),
        71: (0.3585079668674958, 2.3965258596806267, 2.3965258596806267),
        137: (-0.14661333170149543, 2.4810626276615237, 2.4810626276615237),
        74: (-0.7188846912707256, 2.5419958074974476, 2.5419958074974476),
        14: (0.700703103421921, 2.3257645532048867, 2.3257645532048867),
        110: (0.5899029959796849, 2.8252522753129776, 2.8252522753129776),
        17: (-0.5746533895831257, 2.700960778893113, 2.700960778893113),
        83: (-1.202267087126715, 2.0211260823363015, 2.0211260823363015),
        92: (1.1856692804801128, 1.5830609330531038, 1.5830609330531038)
    }),
    39: DirectScoringModel({
        101: (0.5659355899204539, 2.0800943045864186, 2.0800943045864186),
        71: (-0.48989379008109574, 2.3338767139262586, 2.3338767139262586),
        104: (0.1844867286519747, 2.1419425684079068, 2.1419425684079068),
        143: (0.6147995853364414, 1.8484101667023538, 1.8484101667023538),
        23: (0.5123206800906341, 2.0537494051399534, 2.0537494051399534),
        53: (-0.33441852772287084, 2.109071806840893, 2.109071806840893),
        119: (-1.4988919914132337, 1.345051081020651, 1.345051081020651),
        59: (-0.19361444747253287, 2.1430771120472443, 2.1430771120472443),
        92: (0.6427065900271299, 1.5595647349007453, 1.5595647349007453)
    }),
    41: DirectScoringModel({
        143: (0.9608744126449987, 1.7207353442449844, 1.7207353442449844),
        113: (-0.24799300805531557, 2.056510548562579, 2.056510548562579),
        146: (-0.5540784386208669, 1.954725688879509, 1.954725688879509),
        50: (-0.9312685964048173, 1.108488874528371, 1.108488874528371),
        149: (-0.18383638659817528, 2.3700111653773814, 2.3700111653773814),
        56: (0.18028656945016203, 2.0769347003878083, 2.0769347003878083),
        89: (-1.1194899569468488, 1.4799094446670913, 1.4799094446670913),
        92: (1.0308228147565888, 1.4012675012082016, 1.4012675012082016),
        125: (0.8675959998020484, 1.9492796855438637, 1.9492796855438637)
    })
}

mehestan_scaled_models = dict()
zero_shifted_models = dict()

standardized_models, global_model = dict(), DirectScoringModel()
displayed_models, displayed_global_model = dict(), DirectScoringModel()
