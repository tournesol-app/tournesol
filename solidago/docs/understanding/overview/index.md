# Overview of algorithmic governance

## Users and entities

Tte problem of algorithmic governance is to enable 
a set $\texttt{Users}$ of users to collaboratively make decisions.
In **Solidago**, we usually assume that they do so 
by collectively scoring elements $e$ of a set $\texttt{Entities}$ of entities.
Users and entities may have associated metadata, e.g. name, title, publisher...
While in some settings, such as Presidential elections,
it suffices to then only select the best entity $e \in \texttt{Entities}$,
numerous others settings, 
from parlement election to scientific peer reviewing, jury selection and content recommendation,
make abondant use of the scoring of many entities.

## Users' ballots

To collaboratively evaluate entities $e \in \texttt{Entities}$,
the preferences of users $u \in \texttt{Users}$ may be *elicited* in a number of ways,
including: 

- direct assessments of entities, typically like/dislike or 5-star ratings.
- comparisons between pairs of entities, which may quantified comparisons (how much $e$ is better than $f$?).
- rankings of a set of entities, which may only a partial ordering.
- selection of the best within a set of entities.

Furthermore, each evaluation of the sorts may be performed 
with respect to a certain evaluation **criterion** $c \in \texttt{Criterion}$.
Each evaluation may aslo be accompanied with more metadata, 
such as timestamp, used device, maximal and/or minimal values, and so on.

!!! info "Version"
    In version **{__version__}** of **Solidago**, only direct assessments and comparisons were considered.

In all of the above cases, a user $u$ participates to algorithmic governance
by providing a list of tuples $(u, c, E, v)$, 
where $c \in \texttt{Criterion}$ is the criterion that is being evaluated,
$E \subset \texttt{Entities}$ is a subset of evaluated entities
(whose cardinality may be imposed by the kind of evaluation),
and $v$ is the reported value of the comparison.
A timestamp $t$ may be added to the tuple.
The list of all tuples submitted by user $u$ forms the user's $\texttt{Ballot}_u$.

By default, **Solidago** considers that if a user submits 
two tuples $(u, c, E, v, t)$ and $(u, c, E, v', t')$ with $t' > t$,
then the second tuple cancels the former.
As a result, instead of a list of tuples, 
the user's ballot may be viewed as a tuple of *sparse tensors*.
More precisely, direct assessments form a tensor 
$(\texttt{Assessments}_{uce})_{u,c,e}$,
where $\texttt{Assessments}_{uce} = \perp$ meaning that 
no direct assessment of entity $e$ on criterion $c$ was provided by user $u$.
Similarly, the list of comparisons is a sparse tensor 
$(\texttt{Comparisons}_{ucef})_{u,c,e,f}$,
with antisymmetry when inverting the compared entities,
i.e. $\texttt{Comparisons}_{ucfe} = - \texttt{Comparisons}_{ucef}$.

!!! info "Ballot-cutting"
    The principle of a single ballot per user however raises privacy concerns.
    Even if a user is anonymized, 
    the fact that the ballot reveals many of the user preferences
    implies risks of user reidentification.
    To mitigate this risk, a proposed solution is [ballot-cutting](../privacy/ballot_cutting.md).

## Scoring models

One of the key features of **Solidago** is to turn users' ballots $\texttt{Ballot}$
into both user and global *scoring models*.
A scoring model essentially defines a function $\texttt{Entities} \to \mathbb R$,
i.e. it assigns a score to entities.
A user's scoring model is a learning and generalization of the user's preferences,
while the global model aims to describe the aggregation of all users' preferences.

In **Solidago**, we systematically track score uncertainties,
to account for the fact that some users may have provided more information about their preferences
than others who might have been insufficiently active, 
e.g. the latters might have provided an empty ballot.
To account for uncertatines, we accompany scores with left and right uncertainties 
(see link TBD).

We also account for *partial* scoring models, 
i.e. some models may score only a subset of all entities.
Typically, a non-generalizing scoring model based on direct assessments 
may simply score assessed entities, with the corresponding assessment.

Thus, overall, **Solidago** aims to construct a map
$\texttt{Ballots} \mapsto (\texttt{UserModels}, \texttt{GlobalModel})$,
though more information may be used in inputs,
and more information may be returned in outputs.
In practice, **Solidago** proposes a modular construction of such a map,
which allows a more careful analysis of the properties of the map,
as well as improvements of each module separately.
Below, we further briefly discuss some of the key modules.

## Preference learning

User evaluations may be assumed to be noisy.
In practice, inconsistencies are even observed in the Tournesol dataset,
with users favoring $e$ over $f$, $f$ over $g$ and $g$ over $e$.
Moreover, it could be desirable to *generalize* a user's judgment to non-evaluated entities.
Typically, if we strongly assume entity $f$ to resemble entity $e$ (e.g. because of metadata),
and if the user's ballot clearly shows strong preferences for $e$,
then it could be reasonable to assume that they probably regard $f$ favorably too.

## Preference scaling


## Preference aggregattion


## Trust and voting rights


## User and entity clustering
