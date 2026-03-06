def test_svd_user_generator():
    from solidago.primitives.random import Normal, Bernoulli
    from solidago import generators
    n_users = 10
    users = generators.users.New(n_users, Normal(5)).fn()
    users = generators.users.AddColumn("trustworthy", Bernoulli(0.8)).fn(users)
    users = generators.users.BernoulliPretrust(0.2).fn(users)
    assert len(users) == n_users
    for user in users:
        assert user["trustworthy"] or not user["pretrust"]

def test_erdos_renyi_vouch_generator():
    from solidago.primitives.random import Normal, Bernoulli, Zipf
    from solidago.poll.poll_tables import Socials
    from solidago import generators
    n_users = 10
    users = generators.users.New(n_users, Normal(5)).fn()
    users = generators.users.AddColumn("trustworthy", Bernoulli(0.8)).fn(users)
    users = generators.users.BernoulliPretrust(0.2).fn(users)
    users = generators.users.AddColumn("expected_n_vouches", Zipf(1.5)).fn(users)
    socials = generators.socials.ErdosRenyiVouch().fn(users, Socials())
    for social in socials:
        assert users[social["by"]]["trustworthy"] == users[social["to"]]["trustworthy"]
    
def test_svd_entity_generator():
    from solidago.primitives.random import Normal
    from solidago import generators
    entities = generators.entities.New(100, Normal(5)).fn()
    assert len(entities) == 100

def test_evaluation_generator():
    from solidago import generators
    from solidago.generators.engagements.select_entities import BiasedByScore
    from solidago.primitives.random import Normal, Zipf, Add, Poisson, Uniform

    users = generators.users.New(10, Normal(5)).fn()
    entities = generators.entities.New(100, Normal(5)).fn()

    users = generators.users.AddColumn("n_evaluated_entities", Add([Zipf(1.5), Poisson(3.0)])).fn(users)
    users = generators.users.AddColumn("engagement_bias", Normal()).fn(users)
    users = generators.users.AddColumn("p_public", Uniform()).fn(users)
    users = generators.users.AddColumn("p_rate", Uniform()).fn(users)
    users = generators.users.AddColumn("n_comparisons_per_entity", Uniform(1.0, 5.0)).fn(users)

    engagement_generator = generators.engagements.Independent(BiasedByScore(Normal()))
    public_settings, empty_ratings, empty_comparisons = engagement_generator.fn(users, entities)
    rating_generator = generators.ratings.Independent(generators.ratings.Noisy(Normal()))
    ratings = rating_generator.fn(users, entities, public_settings, empty_ratings)
    comparison_generator = generators.comparisons.Independent(generators.comparisons.KnaryGBT(21, 10))
    comparisons = comparison_generator.fn(users, entities, public_settings, empty_comparisons)
    assert len(ratings) > 0
    assert len(comparisons) > 0
    assert all(isinstance(r["value"], float) for r in ratings), ratings