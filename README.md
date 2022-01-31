# Tournesol

This repository hosts the free and open source code of the Tournesol platform.

Learn more about the project on our [Wiki][tournesol-wiki], or meet our community
on [Discord][tournesol-discord-join].

---

**Table of Content**

 - [Structure of the repository](#structure-of-the-repository)
 - [Set-up](#set-up)
 - [Contributing](#contributing)
 - [Licenses](#licenses)

## Structure of the repository

- [analytics](./analytics) contains tools to analyse Tournesol data
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

## Contributing

See the [CONTRIBUTING.md](./CONTRIBUTING.md) file.

### Contributors

The code source of the project exists thanks to
[all people who generously took the time to contribute][tournesol-github-contributors].

Thank you very much!

## Licenses

The Tournesol project has chosen to distribute its software and its other
productions under the terms of different licenses.

See the [LICENSE.md](./LICENSE.md) file for the exhaustive list.

[tournesol-discord-join]: https://discord.gg/WvcSG55Bf3

[tournesol-wiki]: https://wiki.tournesol.app/
[tournesol-wiki-contribute]: https://wiki.tournesol.app/wiki/Contribute_to_Tournesol

[tournesol-github-contributors]: https://github.com/tournesol-app/tournesol/graphs/contributors
