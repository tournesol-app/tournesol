This project is developped and built with [Vite](https://vite.dev), using [React](https://react.dev), [Redux](https://redux.js.org/) and [Redux Toolkit](https://redux-toolkit.js.org/).

## Setup

### Start the development server using the "dev-env" (recommended)

Follow the instructions in [dev-env](../dev-env/README.md)  
Both the frontend and the backend development servers will be started in docker containers.

### Start the development server locally

This setup assumes that an API server is already configured.  
URLs and credentials can be configured in [.env.development](./.env.development).

Requirements:
 * Node.js 18
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


## Learn More

You can learn more in the [Vite documentation](https://vitejs.dev/guide/).

To learn React, check out the [React documentation](https://react.dev/learn).

## Copyright & License

### Source code

Copyright 2021-2023 Association Tournesol and contributors.

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

See the full legal code [AGPL-3.0-or-later][lic-frontend-agpl-3.0-or-later].

### Images

#### Tournesol criteria icons

    Copyright 2021 Association Tournesol - Author Chris Vossen

    Tournesol Criteria Icons are licensed under the
    Creative Commons Attribution 4.0 International (CC BY 4.0).

    You are free to share, copy and redistribute the material in any medium
    or format, and/or to adapt remix, transform, and build upon the material
    for any purpose, even commercially, as long as you give appropriate
    credit, provide a link to the license, and indicate if changes were made.
    You may do so in any reasonable manner, but not in any way that suggests
    the licensor endorses you or your use.

    You should have received a copy of the license along with this
    work. If not, see <https://creativecommons.org/licenses/by/4.0/>.

See the full legal code [CC BY 4.0][lic-frontend-cc-by-4.0].

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

[lic-frontend-agpl-3.0-or-later]: ./LICENSE.AGPL-3.0-or-later.txt
[lic-frontend-cc-by-4.0]: ./LICENSE.CC-BY-4.0.txt
[lic-frontend-mpl-2.0]: ./LICENSE.MPL-2.0.txt

#### Firefox browser logo

    Copyright 2019 Mozilla Corporation

    Firefox Browser logo is licensed under the
    Mozilla Public License Version 2.0 (MPL 2.0).

    You should have received a copy of the license along with this
    work. If not, see <https://www.mozilla.org/en-US/MPL/2.0/>.

See the full legal code
[Mozilla Public License Version 2.0][lic-frontend-mpl-2.0].

Affected materials:
- `public/logos/Fx-Browser-icon-fullColor.svg`

#### Edge browser logo

    Copyright 2019 Microsoft Corporation

Affected materials:
- `public/logos/Edge-Browser-icon-fullColor.svg`

### Texts

The specific texts of the front end's Terms of Service and the Privacy Policy
are dedicated to the public domain as stated by the license Creative Commons
Zero v1.0 Universal.

See the [human-readable disclaimer][cc0-1.0-disclaimer], or the
[full legal code][cc0-1.0-full-legalcode] for more information.

[cc0-1.0-disclaimer]: https://creativecommons.org/publicdomain/zero/1.0/
[cc0-1.0-full-legalcode]: https://creativecommons.org/publicdomain/zero/1.0/legalcode
