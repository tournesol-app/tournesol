# Architecture Knowledge Management

* Status: **accepted** 
* Deciders: [@aidanjungo][gh-aidanjungo], [@amatissart][gh-amatissart],
  [@GresilleSiffle][gh-gresillesiffle], [@lenhoanglnh][gh-lenhoanglnh],
  [@lfaucon][gh-lfaucon], [@jstainer-kleis][gh-jstainer-kleis]
* Date: 2021-12-12

Contents:

* [Summary](#summary)
  * [Issue](#issue)
  * [Decision](#decision)
* [Details](#details)
  * [Assumptions](#assumptions)
  * [Constraints](#constraints)
  * [Positions](#positions)
  * [Arguments](#arguments)
  * [Implications](#implications)
* [Related](#related)
  * [Related decisions](#related-decisions)
  * [Related requirements](#related-requirements)
  * [Related artifacts](#related-artifacts)
  * [Related principles](#related-principles)
* [Notes](#notes)

## Summary

### Issue

At the time of writing, the Tournesol platform has been structured by multiple
software design choices, and none of them are documented.

This knowledge only lives in the team members' memories, and therefore is not
easily accessible.

How to manage this knowledge?

### Decision

Create an Architecture Decision Log (A.D.L.) in a `docs` section of the the
Tournesol mono-repository.

## Details

### Assumptions

We want to document our decisions and to be able to easily share them.

We want to be able to refer to them, both orally and in writing, and enforce
them when needed.

### Constraints

The A.D.L. should be easy to access for anyone.

The A.D.L. should be readable in a browser, without requiring to install Git.

The A.D.L. should explain how to add new architecture decision records (A.D.R.).

### Positions

We considered two options:

(1) using a dedicated Git repository to host the A.D.L.

(2) creating the A.D.L. inside a `docs` section of the Tournesol
mono-repository.

### Arguments

In software development, the A.D.L. is a common and well documented
architecture knowledge management  solution.

The decisions will be openly available on GitHub.

The decisions have a better chance to be read an maintained if there are in
the same repository as the Tournesol platform.

The lifecycle of a decision can be tracked directly in the main Kanban board
of the project: like logging a new decision, making an old one deprecated,
etc. 

### Implications

The A.D.R. must be written in `Markdown` to allow GitHub to display them
nicely.

The A.D.R. should follow, as far as possible, the same template.

The A.D.R. should not be edited after they have been published.

Changing an existing A.D.R. status is allowed, as long as it reflects the team
decision. For instance, a status can evolve from `accepted` to `deprecated` or
`superseded by`.

## Related

### Related decisions

We expect our future important architecture decisions and software design
choices to be added as A.D.R.

### Related requirements

We need to add a `docs` sub-folder in the Tournesol mono-repository.

We need to document how to add a new A.D.R., how to name it, and how to
organize its content.

### Related artifacts

The A.D.L. [README.md](../README.md) will contain instructions explaining how
to add new A.D.R.

### Related principles

The Tournesol association values transparency, benevolence, and pedagogy.

Creating an A.D.L. will help to describe how our software work, in order to
openly share our accumulated knowledge, and to get feedback from the Tournesol
community.

## Notes

More information about A.D.L. and A.D.R. in the following GitHub repository:
- https://github.com/joelparkerhenderson/architecture-decision-record

[gh-aidanjungo]: https://github.com/aidanjungo
[gh-amatissart]: https://github.com/amatissart
[gh-gresillesiffle]: https://github.com/gresillesiffle
[gh-jstainer-kleis]: https://github.com/jstainer-kleis
[gh-lenhoanglnh]: https://github.com/lenhoanglnh
[gh-lfaucon]: https://github.com/lfaucon
[gh-sandre35]: https://github.com/sandre35
