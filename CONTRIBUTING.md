# Contributing to Tournesol

Tournesol is a collective project made possible by the contributions of many
donors and volunteers. We would love for you to help us in this adventure to
make the project even better.

**Table of Content**

- [Code of Conduct](#code-of-conduct)
- [Efficient Ways to Contribute](#efficient-ways-to-contribute)
  - [Add new comparisons](#add-new-comparisons)
  - [Consider donation](#consider-donation)
  - [Talk about Tournesol to your friends](#talk-about-tournesol-to-your-friends)
- [Got a question or Problem?](#got-a-question-or-problem)
- [Found a bug?](#found-a-bug)
- [Missing Feature?](#missing-feature)

**Working on the Source Code**

- [Working on the Source Code](#working-on-the-source-code)
  - [The development process / Asking for review](#the-development-process--asking-for-review)
  - [Development guidelines](#development-guidelines)
    - [Back end](#back-end)
    - [Front end](#front-end)
  - [Translation](#translation)

---

## Code of Conduct

Help us keep Tournesol open and inclusive. Please read and follow our
[Code of Conduct](./CODE_OF_CONDUCT.md).

## Efficient Ways to Contribute

### Add new comparisons

Everyone can greatly help the project by
[submitting new comparisons][ts-compare] in the application 🌻

Comparisons are the cornerstones of Tournesol. They are used to provide
better recommendations and to create an open database to help the research
on ethics of algorithms and large scale recommender systems.

### Consider making a donation

The Tournesol team is small, mainly composed of volunteers. Every
donation counts for us.

With more support we can improve the project, by hiring new developers to
speed up the development of the application, creating partnership to make
Tournesol more visible on the internet, etc.

If you would like to support us, please refer to [the donation page][ts-donate].

### Talk about Tournesol to your friends

With a bigger community Tournesol can improve its recommendations and the
quality of its open database.

Tournesol behaves as the algorithmic representative of its community. The more
the community is big and diverse, the more the recommendation and the database
will be representative of a larger scale of the population opinion.

Talking about Tournesol to your friends can help the project to transform from
a small initiative to a broadly known step in the ethics of algorithms and
large scale recommender systems research.

## Got a Question or Problem?

Please do not open issues for general support questions as we want to keep
GitHub issues for bug reports.

We collect and answer questions on [Discord][ts-discord-join], in the
dedicated channels. This way all the community can benefit from your question
and also provides answers.

## Found a Bug?

If you find a bug in the application or in the source code, you can help us by
submitting an issue to our [GitHub Repository][ts-github-repo]. Even better,
if you are a programmer with spare time you can submit a Pull Request with a
fix.

## Missing Feature?

You can request a new feature by submitting a suggestion on
[Discord][ts-discord-join]. We read all suggestions, even if we may not have
the time to comment each of them.

To review the suggestions, we first evaluate their value for the whole
community, their complexity, and where they fit in the project's roadmap.

When a suggestion is accepted we create ourselves the GitHub issues, and we
mention them in the appropriate Discord threads.

## Working on the Source code

### The development process / Asking for review

You can track progress of the code development in the dedicated
[kanban board][ts-github-kanban].

Anyone can submit ideas that seem relevant, by creating new issues and
placing them inside the column `Ideas / Backlog`.

The core team will then decide which issues have to be handled first. The
prioritized issues are placed in the column `Ready`. One can assign himself to
an issue after having discussed with either the **@core-team** on Discord or the
**@tournesol-app/maintainers** on GitHub.

When your work is in a stable state, you can open a PR from your branch to the
`main` branch on GitHub. You can also ask the maintainers to review your PR
even if the PR is in a draft state. They may give you feedbacks to continue on
the same track or to change the architecture of your current work.

Adding a description in the PR will greatly ease the review process. Please,
take the time to describe the choices you've made, and to explain why.

When your PR is in its final state, notify the maintainers in the PR description
with @tournesol-app/maintainers. Merging is enabled only if someone has
approved your PR.

Changes on the backend must have one or more dedicated tests, to track desired
and undesired behaviour of your feature.

On the frontend, after doing some changes, tests are not compulsory but are
welcomed.

Creation of end-to-end tests is not done on a weekly basis. If you want to
add one, discuss it with the maintainers to debate about the relevance of
this test.

To keep track of progress, bugs of the project, join the
[discord][ts-discord-join]

### Development guidelines

#### Back end

When the back end API is updated, the front end must re-generate its local
client to match the new API schema.

**step 1** While the back end is running, from the root of the front end
folder run the command `yarn run update-schema`. This will update front
end representation the back end OpenAPI schema.

**step 2** Add and commit the updated `openapi.yaml` file.

**step 3** Don't forget to re-generate the service files by running
`scripts/generate-services-from-openapi.sh`

If you're using `dev-env` you can update the schema and the service files by running the script
`dev-env/update-openapi.sh`.

#### Front end

To correct the lint of frontend files, it is possible to activate plugin
directly in your IDE. Otherwise the comamnd `yarn lint:fix` enables you to correct lint
automatically.

**Tips**:
- Tournesol relies a lot on caching for performance, but it may hinder development in some
contexts. It may be helpful to check the option "Disable Caching" in the Netwrok tab of your
browser's developper tools.

### Translation

Tournesol is currently available in English and French. When submitting
changes that involve new texts, please ensure that translation keys
are defined and localized messages are updated, for English at least.
Reviewers can help with the translation to French if necessary.

On the frontend, translations are handled by `react-i18next`.

- [This guide](https://react.i18next.com/guides/quick-start#translate-your-content)
  may be useful to learn how to integrate translated content into React components.
- To extract the new translation keys, use [`yarn i18n:parse`](./frontend/README.md#yarn-i18nparse)

[ts-donate]: https://tournesol.app/about/donate
[ts-compare]: https://tournesol.app/comparison
[ts-github-repo]: https://github.com/tournesol-app/tournesol
[ts-github-kanban]: https://github.com/tournesol-app/tournesol/projects/9
[ts-discord-join]: https://discord.gg/WvcSG55Bf3
