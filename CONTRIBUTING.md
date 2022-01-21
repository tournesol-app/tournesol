# Contributing to Tournesol

## The development process / Asking for review
You can track progress of the project of the following [board](https://github.com/tournesol-app/tournesol/projects/9)

Anyone can create ideas that seems relevant, by creating a new issue and placing it inside the column`Backlog and ideas`.

Then the core-team will decide which issues have to be handled first and available issues are placed in the column `Ready`. One can assigned himself on one ticket after discussing with [maintainers][maintainers].

When your work is in a stable state, you can open a PR from your branch to the `main` branch on Github. You can also ask [maintainers][maintainers] to review your PR even if the PR is in a draft state. They may give you feedbacks to continue on the same track or to change the architecture of your current work.

Adding a description in the PR will greatly ease the review process. Please, take the time to describe the choices you've made, and to explain why. 

When your PR is in its final state, ask at least one of [maintainers][maintainers] to review it. Merging is enabled only if someone has approved your PR.

One change on the backend must have one or more dedicated tests, to track desired and undesired behaviour of your feature.

On the frontend, after doing some changes, tests are not compulsory but are welcomed.

Creation of end-to-end test is not done on a weekly basis. If you want to add one, discuss about it with [maintainers][maintainers] to debate about the relevance of this test.

To keep track of progress, bugs of the project, join the [discord][tournesol-discord-join]

# Tips

- One change on the backend must have a dedicated test (create a new test, or modify a existing one). The command `pytest` enables to lauch all tests.
Moreover the command `pytest --html=report.html –self-contained-html` enables to create a clean html report document with details of logs for each test.

When the back end API is updated, the front end must re-generate its local client to match the new API schema.

**step 1** While the back end is running, from the root of the front end folder run the command `yarn run update-schema`. This will update front end representation the back end OpenAPI schema.

**step 2** The re-generate the service files by running `scripts/generate-services-from-openapi.sh`

- To correct the lint of frontend files, it is possible to activate plugin directly in your IDE. Otherwise the comamnd `yarn lint:fix` enables you to correct lint automatically.

[tournesol-discord-join]: https://discord.gg/WvcSG55Bf3
[maintainers]: https://github.com/orgs/tournesol-app/teams/maintainers