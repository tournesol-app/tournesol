# Tournesol

This repository host the free and open source code of the Tournesol platform.

Learn more about the project on our [Wiki][tournesol-wiki], or meet our community
on [Discord][tournesol-discord-join].

## Structure of the repository

- [docs](./docs) contains different kinds of documentations related to the
  project
- [dev-env](./dev-env) contains the info to create the Tournesol development
  environment with docker-compose
- [backend](./backend) is a Django application that serves as Tournesol's API
- [frontend](./frontend) is a React JS application which is the main website
  and a frontend to Tournesol's API
- [infra](./infra) contains an ansible recipe used to configure the servers
  running Tournesol
- [browser-extension](./browser-extension) is a JavaScript extension for
  Google Chrome and Mozilla Firefox
- [tests](./tests) contains end-to-end tests for Tournesol

## Set-up

Please refer to the `dev-env` directory or the corresponding documents in
`frontend` and `backend` directories.

## Contribute

See the Wiki page [Contribute to Tournesol][tournesol-wiki-contribute] for
details.

[tournesol-discord-join]: https://discord.gg/WvcSG55Bf3
[tournesol-wiki]: https://wiki.tournesol.app/
[tournesol-wiki-contribute]: https://wiki.tournesol.app/index.php/Contribute_to_Tournesol
