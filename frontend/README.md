This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app), using the [Redux](https://redux.js.org/) and [Redux Toolkit](https://redux-toolkit.js.org/) template.

## Setup

### Start the development server using the "dev-env" (recommended)

Follow the instructions in [dev-env](../dev-env/README.md)  
Both the frontend and the backend development servers will be started in docker containers.

### Start the development server locally

This setup assumes that an API server is already configured.  
URLs and credentials can be configured in [.env.development](./.env.development).

Requirements:
 * Node.js 14
 * yarn

Setup:
1. In this folder, install frontend dependencies: `yarn install`
2. Generate the OpenAPI client with the script `./scripts/generate-services-from-openapi.sh`
3. Start the local development server: `yarn start`

## Available Scripts

In the project directory, you can run:

### `yarn install`

Install all dependencies from `package.json`

### `yarn start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `yarn lint`

Runs the linter and returns lint errors.

This check is automatically enforced on commit using a pre-commit hook. Use `git commit --no-verify` to bypass this check (e.g. to commit on a branch with work in progress).

### `yarn lint:fix`

Attempts to fix lint problems automatically using `eslint --fix`.<br />
This is especially useful to apply `prettier` format rules, if they are not enforced by your IDE.

### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn i18n:parse`

Parses source code to extract all translation keys used in frontend, and updates the translation catalogs accordingly in `public/locales`.

### `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `yarn eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

## Copyright & License

### Source code

Copyright 2021-2022 Association Tournesol and contributors.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

See the full legal code [AGPL-3.0-or-later][lic-agpl-3.0-or-later].

### Images

#### Firefox Browser logo

    Firefox Browser logo - Copyright by Mozilla Corporation

    Firefox Browser logo is licensed under the
    Mozilla Public License Version 2.0.

    You should have received a copy of the license along with this
    work. If not, see <https://www.mozilla.org/en-US/MPL/2.0/>.

See the full legal code [Mozilla Public License Version 2.0][lic-frontend-mpl-2.0].

Affected materials:
- `public/logos/Fx-Browser-icon-fullColor.svg`

#### Tournesol Criteria Icons

    Tournesol Criteria Icons - Copyright by Chris Vossen

    Tournesol Criteria Icons are licensed under the
    Creative Comons Attribution-ShareAlike 4.0 International
    (CC BY-SA 4.0) License.

    You should have received a copy of the license along with this
    work. If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.


See the full legal code [CC BY-SA 4.0][lic-cc-by-sa-4.0].

Affected materials:
- `public/images/criteriaIcons/reliability.svg`
- `public/images/criteriaIcons/pedagogy.svg`
- `public/images/criteriaIcons/importance.svg`
- `public/images/criteriaIcons/layman_friendly.svg`
- `public/images/criteriaIcons/entertaining_relaxing.svg`
- `public/images/criteriaIcons/engaging.svg`
- `public/images/criteriaIcons/diversity_inclusion.svg`
- `public/images/criteriaIcons/better_habits.svg`
- `public/images/criteriaIcons/backfire_risk.svg`

[lic-agpl-3.0-or-later]: ./LICENSE.AGPL-3.0-or-later.txt
[lic-cc-by-sa-4.0]: ./LICENSE.CC-BY-SA-4.0.txt
[lic-frontend-mpl-2.0]: ./LICENSE.MPL-2.0.txt
