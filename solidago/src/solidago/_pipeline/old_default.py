@dataclass
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
    voting_rights: VotingRightsAssignment = AffineOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    )
    preference_learning: PreferenceLearning = UniformGBT(
        prior_std_dev=7,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
    )
    scaling: Scaling = ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_activity=10.0,
            n_scalers_max=100,
            privacy_penalty=0.5,
            p_norm_for_multiplicative_resilience=4.0,
            error=1e-5
        ),
        QuantileZeroShift(
            zero_quantile=0.15,
            lipschitz=0.1,
            error=1e-5
        ),
        Standardize(
            dev_quantile=0.9,
            lipschitz=0.1,
            error=1e-5
        )
    )
    aggregation: Aggregation = EntitywiseQrQuantile(
        quantile=0.2,
        lipschitz=0.1,
        error=1e-5
    )
    post_process: PostProcess = Squash(
        score_max=100
    )


