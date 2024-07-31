<h1 align="center">Tournesol - Collaborative Content Recommendations</h1>

<p align="center">
  <img
    src="./frontend/public/logos/Tournesol_Logo.png"
    alt="tournesol-logo"
    width="120px"
    height="120px"
  />
<p>
<p align="center">
  <i>
    Tournesol is a free software designed to collaboratively identify public
    interest videos that should be largely recommended.
  </i>
</p>
<p align="center">
  <i>
    Participants are invited to judge the videos' quality, and build together
    an open database to help the research in AI ethics and recommendation
    systems.
  </i>
</p>

<p align="center">
  <a href="https://tournesol.app"><strong>https://tournesol.app</strong></a>
  <br>
</p>

<p align="center">
  <a href="https://tournesol.app/comparison">Compare Videos</a>
  ·
  <a href="./CONTRIBUTING.md">Contributing Guidelines</a>
  ·
  <a href="https://tournesol.app/about/donate">Make a Donation</a>
  <br>
</p>

---

This repository hosts the source code of the Tournesol platform.

To learn more about our participatory research project and its platform, join
us on [Discord][tournesol-discord-join].

**Table of Content**

 - [Structure of the repository](#structure-of-the-repository)
 - [Set-up](#set-up)
 - [Contributing](#contributing)
 - [Security](#security)
 - [Copyright & Licenses](#copyright--licenses)

## Structure of the repository

- [backend](./backend) is a Django application that serves as Tournesol's API
- [browser-extension](./browser-extension) is a JavaScript extension for
  Google Chrome and Mozilla Firefox
- [data-visualization](./data-visualization) contains a Streamlit app to
  visualize the Tournesol public data
- [dev-env](./dev-env) contains the info to create the Tournesol development
  environment with docker-compose
- [docs](./docs) contains different kinds of documentations related to the
  project
- [frontend](./frontend) is a React JS application which is the main website
  and a frontend to Tournesol's API
- [infra](./infra) contains an ansible recipe used to configure the servers
  running Tournesol
- [solidago](./solidago/) the library that implements Tournesol algorithms
- [tests](./tests) contains end-to-end tests for Tournesol

## Set-up

Please refer to the `dev-env` directory or the corresponding documents in
`frontend` and `backend` directories.

## Contributing

### Code of Conduct

Help us keep Tournesol open and inclusive. Please read and follow our
[Code of Conduct](./CODE_OF_CONDUCT.md).

### Contributing Guidelines

Read through our [contributing guidelines](./CONTRIBUTING.md) to learn about
the different ways to help the project.

### Contributors

The code source of the project exists thanks to
[all people who generously took the time to contribute][tournesol-github-contributors].

Thank you very much!

## Security

To report security vulnerabilities follow our [security policy](./SECURITY.md).

## Copyright & Licenses

The Tournesol project has chosen to distribute its software and its other
productions under the terms of different licenses.

See the [LICENSE.md](./LICENSE.md) file for the exhaustive list.

You can find the copyright notice of each software and other production in
their dedicated `README.md` file.

[tournesol-discord-join]: https://discord.gg/WvcSG55Bf3

[tournesol-github-contributors]: https://github.com/tournesol-app/tournesol/graphs/contributors
