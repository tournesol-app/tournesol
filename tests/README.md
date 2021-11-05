# End-to-end tests for Tournesol

An end-to-end tests suite, based on [Cypress](https://www.cypress.io/), for the platform Tournesol and the Tournesol browser extension.

## Requirements

* A local instance of Tournesol, as provided by [dev-env](../dev-env/README.md)
* Node.js 14

### Install the dependencies

```
yarn install --frozen-lockfile
```

## Run the tests

```
yarn run cypress run
```

By default, Cypress will run the tests on Electron (based on Chromium). 
To run the tests in a specific browser installed on your system, use `--browser` :
```
yarn run cypress run --browser firefox
```

To launch the Cypress Test Runner UI:
```
yarn run cypress open
```

For more options see [Cypress documentation](https://docs.cypress.io/guides/guides/command-line#Commands)


## Testing the browser extension

Currently, the browser extension tests support only Chromium and Chrome, and need to be run in "headed" (windowed) mode.  
The tests related to the browser extension will be skipped if these conditions are not met.

```
yarn run cypress run --browser chrome --headed
```

