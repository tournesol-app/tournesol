# Mono vs. multiple Git repositories

* Status: **accepted** 
* Deciders: [@amatissart][gh-amatissart],
  [@GresilleSiffle][gh-gresillesiffle], [@lfaucon][gh-lfaucon],
  [@jstainer-kleis][gh-jstainer-kleis], [@sandre35][gh-sandre35]
* Date: 2021-09-28

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

## Summary

### Issue

The Tournesol platform is composed of an API, and others software depending
on it: a front-end interface, a browser extension, a Twitter bot, etc.

This ecosystem is maintained by a small team, and voluntary contributions.

The source code of some software were previously hosted on the same Git
repository, but has been split in several repositories afterward for a better
clarity.

The team were committed to keeping track of the new problems the split may
raise.

Today deploying the last updated version of each software doesn't always
result in a working platform. Determining the compatibility of each
software is manual and error prone process.

Which repository architecture suits best our needs?

### Decision

Use a mono-repository architecture.

## Details

### Assumptions

We want to ease the development process, the continuous integration and the
deployments.

### Constraints

The maintenance cost of the solution should be light, adapted to our core team
size.

We want to be confident in our deployment. We do not want to have a process
that could not be automated because it would rely on manual inputs.

We want to be confident in our development, and have an easy way to trigger
checks indicating when a new merge will break an existing feature.

### Positions

We considered using a mono-repository architecture.

We considered using a multi-repository architecture. This architecture was the
current architecture before the decision process starts.

### Arguments

We have chosen the mono-repository architecture because it makes the
development process easier, and encourages building a strong continuous
integration (CI) pipeline in GitHub. It will increase the stability of the
Tournesol platform, making it deployable at any point in time.

**development benefits**

The developers pulling the `head` of the mono-repository have a strong chance
to get software compatible with each others. The CI acting as a safeguard in
the mono-repository preventing any merge that would break a specific software.

The developers working on the API will be able to get a complete CI feedback
directly in the pull request of their branch. They will know if the new code
breaks any dependencies. 

The development a full-stack feature is now made possible in a single branch
of a single repository.

**CI benefits**

As maintaining a healthy mono-repository depends on the CI quality, this
architecture also makes the deployments easier and safer.

Deploying the `head` of the repository will deploy software compatible with
each others. No manual investigation will be required to determine if the
deployed Tournesol platform will work.

Having a single CI configuration for a mono-repository is more
maintainable than having several CI configurations dispatched in several
repositories.

**deployment benefits**

The `head` of the deployment recipes will be part of the mono-repository and
will be compatible with the `head` of all software deployed.

Finally, the increase stability of the Tournesol platform will allow the team
to deploy often.

### Implications

The team should develop unit tests for each endpoint of the API.

The team should add component tests in the front end.

The team should add end-to-end tests to check the last version of the front
end against the last version of the API.

The team is encouraged to develop a strong and relatively fast CI pipelines in
GitHub.

Maintainers should be vigilant during code reviews and prevent as far as
possible the code of distinct software to be tightly coupled. 

## Related

### Related decisions

We expect all our software depending on the API, to be added to the
mono-repository.

We expect all our software deployed by our deployment recipes, to be added to
the mono-repository.

We expect to add more software in the mono-repository as long as the team
agrees.

The old repositories will be archived on GitHub:
- tournesol-app/tournesol-backend
- tournesol-app/tournesol-frontend
- tournesol-app/tournesol-infra
- tournesol-app/tournesol-browser-extension

### Related requirements

We need to create the continuous integration pipeline in GitHub, so that it
runs the back end tests, the front end tests, and the end-to-end tests.

### Related artifacts

The folder `.github/workflows` will contain the continuous integration
configuration.

[gh-amatissart]: https://github.com/amatissart
[gh-gresillesiffle]: https://github.com/gresillesiffle
[gh-jstainer-kleis]: https://github.com/jstainer-kleis
[gh-lfaucon]: https://github.com/lfaucon
[gh-sandre35]: https://github.com/sandre35
