# Architecture Decision Log

Welcome in the Tournesol Architecture Decision Log (A.D.L.).

This documentation contains all important architectural decisions, and
software design choices made during the development of the Tournesol platform.

All decisions are captured within individual files, called Architecture
Decision Record (A.D.R.).

Learn more about A.D.R. in [this other documentation][github-adr].

## Usage

### Add a new decision

First, copy the [A.D.R. template](./adr_template.md) in the appropriate
sub-folder.

If this new decision is related to a new topic, create a new sub-folder
instead.

Prefix the newly created file by the date of the decision, following the
format `YYYY_MM_DD_`.

Edit the file and set its status, list the deciders, and add the date.

Finally, describe the decision by following the documentation bellow.

### Template documentation

Our template is an adaptation of the template described by Jeff Tyree and Art
Akerman in _« Architecture Decisions: Demystifying Architecture »_
[[1]][adr-by-jtyree-aakerman-pub].

In order to make a decision state more visible, we moved the status section
at the beginning of the document.

You can find the documentation of each template section in
[this documentation][adr-by-jtyree-aakerman].

You can find several [examples here][github-adr-examples].

## License

No Copyright.

All Architecture Decision Records are available under the term of the license
`CC0 1.0 Universal`.

**human readable summary**

https://creativecommons.org/publicdomain/zero/1.0/

**full legal code**

https://creativecommons.org/publicdomain/zero/1.0/legalcode

[github-adr]: https://github.com/joelparkerhenderson/architecture-decision-record
[github-adr-examples]: https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/examples

[adr-by-jtyree-aakerman]: https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/templates/decision-record-template-by-jeff-tyree-and-art-akerman/index.md
[adr-by-jtyree-aakerman-pub]: https://personal.utdallas.edu/~chung/SA/zz-Impreso-architecture_decisions-tyree-05.pdf
