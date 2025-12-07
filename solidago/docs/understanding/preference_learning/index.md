# Preference learning

Preference learning consists of transforming each [user's ballots](../overview/#users-ballots)
into an algorithmic model of their preferences,
regarding a set of entities to be [evaluated](../overview/).
We also demand that the models estimate the [uncertainties](uncertainty.md) they have,
as these are then essential in the subsequent preference aggregations.

The ballots may consist of direct assessments, comparisons or other signals (e.g. watch time),
given under various contexts.
A good preference learning model should model users' behaviors in various contexts,
could also leverage the data associated to the entities to be evaluated,
and should have mathematical guarantees to provide trustworthiness.
Doing so is still the subject of our ongoing research endeavor.

## Learning from comparisons

Historically, Tournesol started with comparison data only.
Such an approach has also been used by various preference learning projects,
including [The Moral Machine for autonomous car dilemma](https://moralmachines.net/),
[WeBuildAI for food donation](https://dl.acm.org/doi/10.1145/3359283)
and [Reinforcement Learning with Human Feedback for language models](https://en.wikipedia.org/wiki/Reinforcement_learning_from_human_feedback).
All the above projects especially leverage a preference model 
known as the [Bradley-Terry model](comparison_learning.md#bradley-terry).

In the context of Tournesol, however, we additionally favored *quantitative comparisons*,
namely the user can report the extent to which they prefer an entity over another.
This has led to the introduction of the family of [generalized Bradley-Terry models](comparison_learning.md#generalized-bradley-terry) 
[[FFHV, AAAI'24](https://ojs.aaai.org/index.php/AAAI/article/view/30020)].
These models are especially well-behaved,
enabling maximum-a-posteriori existence and uniqueness,
fast computations, monotonicity and Lipschitz resilience.

The models can additionally leverage entity vector embedding or entity similarity,
while preserving some of the properties [[FBBH, NeurIPS'25](https://openreview.net/forum?id=hfKPMjiDnv)].
These new algorithms have not yet been added to Solidago.
Please find out more in our [comparison_learning](comparison_learning.md) page.

## Learning from multiple signals

We are currently investigating algorithms that can learn from multiple preference signals.
