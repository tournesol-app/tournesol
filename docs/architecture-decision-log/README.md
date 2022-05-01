# Architecture Decision Log

Welcome in the Tournesol Architecture Decision Log (A.D.L.).

This documentation contains all important architectural decisions, and
software design choices made during the development of the Tournesol platform.

All decisions are captured within individual files, called Architecture
Decision Record (A.D.R.).

Learn more about A.D.R. in [this other documentation][github-adr].

---

Table of Content

* [What's new](#whats-new)
* [Keywords](#keywords)
* [Usage](#summary)
  * [Rules](#rules)
  * [Add a new decision record](#issue)
  * [Update a decision record's status](#decision)
* [Documentation](#documentation)
  * [The A.D.R. template](#the-ADR-template)
  * [Examples](#examples)
* [License](#license)

## What's new?

See the complete A.D.L. history in the [CHANGELOG.md](./CHANGELOG.md).

## Keywords

**A.D.** - architecture decision

An architecture decision (A.D.) is a software design choice that addresses a
significant requirement.

**A.D.R.** - architecture decision record

An architecture decision record (A.D.R.) is a document that captures an important
architectural decision made along with its context and consequences.

**A.D.L.** - architecture decision log

An architecture decision log (A.D.L.) is the collection of all ADRs created and
maintained for a particular project or organization.

**AKM** - architecture knowledge management

All these are within the topic of architecture knowledge management (A.K.M.).

## Usage

### Rules

Characteristics of a good A.D.R.

- **Point in Time** - Identify when the A.D. was made
- **Rationality** - Explain the reason for making the particular A.D.
- **Immutable record** - The decisions made in a previously published A.D.R.
  should not be altered
- **Specificity** - Each A.D.R. should be about a single A.D.

A new A.D.R. may take the place of a previous A.D.R.

When an A.D. is made that replaces or invalidates existing A.D.R.
- a new A.D.R. should be created ;
- and the status of the old ones should be updated.

### Add a new decision record

First, copy the [A.D.R. template](./adr_template.md) in the appropriate
sub-folder.

If this new decision is related to a new topic, create a new sub-folder
instead.

Prefix the newly created file by the date of the decision, following the
format `YYYY-MM-DD_`.

Edit the file and describe the decision.

Finally, add the decision to the `CHANGELOG.md` 

### Update a decision record's status

If a decision becomes obsolete, or is replaced by a new one, its status must
be updated accordingly.

Edit the A.D.R. and set the status field to **deprecated**, or
**superseded by** followed by a URI pointing to the new decision. Record the
update by adding a new line in the `CHANGELOG.md`.

The URI must point to the last updated version of the new decision. 

Example:

> Status: **superseded by** [2021-12-12 Create an ADL][adr-20211212-create-an-adl]

Raw Markdown:

```markdown
Status: **superseded by** [2021-12-12 Create an ADL](https://github.com/tournesol-app/tournesol/blob/adl/docs/architecture-decision-log/architecture-knowledge/2021_12_12_create_an_adl.md)
```

### Update more section of an A.D.R.?

In theory a published A.D.R. should not be altered.

In practice some information can be added afterward, like missing deciders,
forgotten related artifacts, notes, etc.

These kinds of correction don't require to update the `CHANGELOG.md`.

## Documentation

### The A.D.R. template

Our template is an adaptation of the template described by Jeff Tyree and Art
Akerman in _« Architecture Decisions: Demystifying Architecture »_
[[1]][adr-by-jtyree-aakerman-pub].

In order to make the actual state of a decision more visible, and more
precise, we moved the status section at the beginning of the document, and
added two more fields: deciders and date.

Our [template](./adr_template.md).

### Examples

Several examples of decisions described using the adapted template can be
found in [this repository][github-adr-examples].

## License

No Copyright.

All Architecture Decision Records are available under the term of the license
`CC0 1.0 Universal`.

**human readable summary**

https://creativecommons.org/publicdomain/zero/1.0/

**full legal code**

https://creativecommons.org/publicdomain/zero/1.0/legalcode

[adr-20211212-create-an-adl]: ./architecture-knowledge/2021-12-12_create_an_adl.md

[github-adr]: https://github.com/joelparkerhenderson/architecture-decision-record
[github-adr-examples]: https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/examples

[adr-by-jtyree-aakerman]: https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/templates/decision-record-template-by-jeff-tyree-and-art-akerman/index.md
[adr-by-jtyree-aakerman-pub]: https://personal.utdallas.edu/~chung/SA/zz-Impreso-architecture_decisions-tyree-05.pdf
