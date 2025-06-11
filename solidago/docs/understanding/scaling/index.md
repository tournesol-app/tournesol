# Preference scaling

This challenge is especially exacerbated in *sparse voting* 
[[AGHV24](https://proceedings.mlr.press/v238/allouah24a.html)],
i.e. when most users only evaluate a small fraction of all entities to be evaluated.
We stress that, when considering a large number of entities,
sparse voting is the norm,
e.g. in [Tournesol](https://tournesol.app), 
scientific peer reviewing or online Polis consultations.

This has been called the *French reviewer problem*.
Namely, a "Parisian reviewer" may systematically provide poor ratings,
except for exceptionally good entities.
As a result, entities that are mostly evaluated by Parisian-like reviewers may be under-evaluated,
not because they are especially poor,
but rather because their evaluators were especially negative.
Another issue that arises is the case of "Marseillais reviewers",
namely, reviewers that systematically provide extreme ratings.
Good entities that are primarily evaluated by such reviewers may then top the rankings,
not necessarily because they are the best entities,
but rather because they are evaluated by reviewers who provide extremely high ratings to good entities.

Formally, the Von Neumann-Morgenstern axioms suggest 
that scoring models should be thought as being defined up to a positive affine translation,
that is, for any $\alpha > 0$ and $\beta \in \mathbb R$,
the scoring models $s$ and $\alpha s + \beta$ should be regarded as describing
the same underlying preferences.
Preference scaling is then the problem of selecting a positive affine translation for each user,
so that scaled user models become "on the same scale", 
to then allow for more meaningful preference aggregation.
Note that some preference aggregation modules may not require preference scaling,
e.g. if they are ranking-based (or "ordinal", as is said in the literature).
