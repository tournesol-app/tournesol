def test_random():
    import solidago
    assert isinstance(solidago.load("Bernoulli", solidago.random, p=.4), solidago.random.Bernoulli)
    assert isinstance(solidago.load("Deterministic", solidago.random, value="hello"), solidago.random.Deterministic)
    assert isinstance(solidago.load("Gamma", solidago.random, shape=1.0), solidago.random.Gamma)
    assert isinstance(
        solidago.load("Multinomial", solidago.random, probabilities=[.2, .5, .3], values=["yes", "no", "maybe"]), 
        solidago.random.Multinomial
    )
    assert isinstance(solidago.load("Normal", solidago.random, dimension=5), solidago.random.Normal)
    assert isinstance(solidago.load("Poisson", solidago.random, mean=3.5), solidago.random.Poisson)
    assert isinstance(solidago.load("Uniform", solidago.random, min=5, max=6.7), solidago.random.Uniform)
    assert isinstance(solidago.load("Zipf", solidago.random, power_decay=2), solidago.random.Zipf)
    assert isinstance(
        solidago.load(
            "Add", solidago.random, 
            subdistributions=[["Zipf", dict(power_decay=2.0)], ["Poisson", dict(mean=5.0)]]
        ), 
        solidago.random.Add
    )

def test_select_entities():
    import solidago
    assert isinstance(
        solidago.load("generators.engagements.select_entities.Uniform", solidago),
        solidago.generators.engagements.select_entities.Uniform
    )
    assert isinstance(
        solidago.load("BiasedByScore", solidago.generators.engagements.select_entities, noise=["Normal", dict()]),
        solidago.generators.engagements.select_entities.BiasedByScore
    )

def test_similarity():
    import solidago

def test_minimizer():
    import solidago
    assert isinstance(
        solidago.load("SciPyMinimizer", solidago.minimizer, method="L-BFGS-B", convergence_error=1e-5),
        solidago.minimizer.Minimizer
    )

def test_uncertainty():
    import solidago
    assert isinstance(
        solidago.load("NLLIncrease", solidago.uncertainty, nll_increase=1.0, error=1e-1, max=1e3),
        solidago.uncertainty.NLLIncrease
    )
    assert isinstance(
        solidago.load("UncertaintyByLossIncrease", solidago.uncertainty, loss_increase=1.0, error=1e-1, max=1e3),
        solidago.uncertainty.UncertaintyByLossIncrease
    )
    assert isinstance(
        solidago.load("HessDiagonal", solidago.uncertainty),
        solidago.uncertainty.HessDiagonal
    )


def test_root_law():
    import solidago
    assert isinstance(
        solidago.load("BradleyTerry", solidago.poll_functions.preference_learning.gbt.root_law),
        solidago.poll_functions.preference_learning.gbt.root_law.BradleyTerry
    )
    assert isinstance(
        solidago.load("Uniform", solidago.poll_functions.preference_learning.gbt.root_law),
        solidago.poll_functions.preference_learning.gbt.root_law.Uniform
    )
    assert isinstance(
        solidago.load("Gaussian", solidago.poll_functions.preference_learning.gbt.root_law, std=2.),
        solidago.poll_functions.preference_learning.gbt.root_law.Gaussian
    )
    assert isinstance(
        solidago.load("Discrete", solidago.poll_functions.preference_learning.gbt.root_law, n_values=21),
        solidago.poll_functions.preference_learning.gbt.root_law.Discrete
    )

def test_generators_ratings():
    import solidago
    assert isinstance(
        solidago.load("Noisy", solidago.generators.ratings, distribution=["Normal", dict(std=1.0)]),
        solidago.generators.ratings.Noisy
    )
    assert isinstance(
        solidago.load("Negate", solidago.generators.ratings, honest=["Deterministic", dict()]),
        solidago.generators.ratings.Negate
    )

def test_generators_comparisons():
    import solidago
    assert isinstance(
        solidago.load("KnaryGBT", solidago.generators.comparisons, comparison_max=10),
        solidago.generators.comparisons.KnaryGBT
    )
    assert isinstance(
        solidago.load(
            "Negate", solidago.generators.comparisons, 
            honest=solidago.load("KnaryGBT", solidago.generators.comparisons, comparison_max=10)
        ),
        solidago.generators.comparisons.compare.Negate
    )

def test_poll_functions():
    import solidago
    assert isinstance(
        solidago.load(
            "LipschiTrust", solidago.poll_functions, 
            pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1.0e-8
        ), 
        solidago.poll_functions.LipschiTrust
    )
    assert isinstance(
        solidago.load(
            "Mehestan", solidago.poll_functions, 
            lipschitz=1.0, min_scaler_activity=1.0, n_scalers_max=100, privacy_penalty=0.5,
            user_comparison_lipschitz=10.0, p_norm_for_multiplicative_resilience=4.0,
            n_entity_to_fully_compare_max=100, n_diffs_sample_max=1000,
            default_multiplier_dev=0.5, default_translation_dev=1.0, error=1.0e-2,
        ), 
        solidago.poll_functions.Mehestan
    )
    assert isinstance(
        solidago.load(
            ("AffineOvertrust", dict(privacy_penalty=0.5, min_overtrust=2.0, overtrust_ratio=0.1)), 
            solidago.poll_functions
        ),
        solidago.poll_functions.AffineOvertrust
    )
    assert isinstance(
        solidago.load(solidago.poll_functions.Squash(score_max=100.), solidago.poll_functions),
        solidago.poll_functions.Squash
    )
    
def test_generators():
    import solidago
    assert isinstance(
        solidago.load("users.New", solidago.generators, n_users=5, distribution=["Normal", dict(dimension=5)]), 
        solidago.generators.users.New
    )
    assert isinstance(
        solidago.load("users.AddColumn", solidago.generators, column="trustworthy", distribution=["Bernoulli", dict(p=0.8)]),
        solidago.generators.users.AddColumn
    )
    assert isinstance(
        solidago.load("users.AddColumn", solidago.generators, column="trustworthy", distribution=["Bernoulli", dict(p=0.8)]),
        solidago.generators.users.AddColumn
    )
    assert isinstance(
        solidago.load(
            "engagements.Independent", solidago.generators, 
            select_entities=["BiasedByScore", dict(noise=["Normal", dict()])]
        ),
        solidago.generators.engagements.Independent
    )


def test_pipeline():
    import solidago
    assert isinstance(
        solidago.load("tests/poll_functions/test_pipeline.yaml", solidago.poll_functions),
        solidago.poll_functions.Sequential
    )