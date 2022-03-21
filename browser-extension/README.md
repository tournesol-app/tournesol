# Tournesol browser extension

The extension adds several Tournesol features to the YouTube interface.

Users can directly access the comparison and analysis pages of videos, and can
easily add them to their rate-later list.

<p align="center">
  <a href="https://addons.mozilla.org/en-US/firefox/addon/tournesol-extension/">Install on Mozilla Firefox</a>
  🌻
  <a href="https://chrome.google.com/webstore/detail/tournesol-extension/nidimbejmadpggdgooppinedbggeacla">Install on Chrome</a>
  <br>
</p>

**Table of Content**

- [Development guidelines](#development-guidelines)
  - [Documentation](#documentation)
  - [Install the development tools](#install-the-development-tools)
  - [Code Quality](#code-quality)
  - [Upating the version](#updating-the-version)
- [Release a new version](#release-a-new-version)
- [License](#license)


## Development guidelines

This section contains the development documentations, and the contributing
guidelines we would like every contributor to follow.

### Documentation

The documentations for developing and distributing web extensions are
available here:
- https://developer.chrome.com/docs/extensions/
- https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions

### Install the development tools

```shell
yarn install
```

### Code Quality

We use `ESLint` to find and fix problems in the JavaScript code.

Before submitting new pull requests, run the linter with the following
commands:

```shell
yarn lint

# automatically fix problems
yarn lint --fix
```

### Updating the version

This project adheres to [Semantic Versioning][semantic-versioning].

Given a version number `MAJOR.MINOR.PATCH`, increment the:

- `MAJOR` version when backwards **incompatible** changes are made
- `MINOR` version when new backwards **compatible** functionalities are added
- `PATCH` version for backwards **compatible** bug fixes

## Release a new version

To release the extension on Chrome or Mozilla Firefox, run the script `./build.sh`
and upload the generated .zip file in the corresponding extension web store.

## License

See the [LICENSE.md](./src/LICENSE) file.

[download-chrome]: https://chrome.google.com/webstore/detail/tournesol-extension/nidimbejmadpggdgooppinedbggeacla
[download-firefox]: https://addons.mozilla.org/en-US/firefox/addon/tournesol-extension/

[semantic-versioning]: https://semver.org/
