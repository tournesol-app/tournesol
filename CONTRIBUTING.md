# Process of development / Asking for review

You can track progress of the project of the following [board](https://github.com/tournesol-app/tournesol/projects/9)

Anyone can create ideas that seems relevant, by creating a new issue and placing it inside the column`Backlog and ideas`.

Then the core-team will decide which issues have to be handled first and available issues are placed in the column `Ready`. One can assigned himself on one ticket after discussing with [Adrien][Adrien], [Romain][Romain]. or [Louis][Louis].

When you work is in a stable state, you can open a PR from your branch to `main` on Github. You can also ask [Adrien][Adrien] or [Romain][Romain] your PR even if the PR is in a draft state. They may give you feedbacks to continue on the same tracks or to change the architecture of your current work.

When your PR is in its final state, ask [Adrien][Adrien], [Romain][Romain] and [Louis][Louis] to review it (at least). Merging is enabled only if someone has approved your PR.

One change on the backend must have a dedicated test, to track desired and undesired behaviour of your feature.

On the frontend, after doing some changes, test are not compulsory but are welcomed.

Creation of end to end test is not done on a weekly basis. If you want to add one, discuss about it with [Adrien][Adrien] and [Romain][Romain]  to debate about the relevance of this test.

To keep track of progress, bugs of the project, join the [discord][tournesol-discord-join]

# Tips

- One change on the backend must have a dedicated test (create a new test, or modify a existing one). The command `pytest` enables to lauch all tests.
However the command `pytest --html=report.html –self-contained-html` enables to create a clean html report document with details of logs for each test.

- To update OpenApi content, and specifically `.yaml`, you first have to launch de backend. Then, on the frontend you can type the following command `yarn run update-schema`.

- To update typescript file that depends on the content of `.yaml`, you have to go the folder `scripts` of frontend and type the command `./generate-services-from-openapi.sh`.

- To correct the lint of frontend files, it is possible to activate plugin directly in your IDE. Otherwise the comamnd `yarn lint:fix` enables you to correct lint automatically.

[tournesol-discord-join]: https://discord.gg/WvcSG55Bf3
[Adrien]: https://github.com/amatissart
[Romain]: https://github.com/GresilleSiffle
[Louis]: https://github.com/lfaucon
