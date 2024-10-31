# Tournesol back end

The API of the Tournesol platform, made with Python and Django.

**Table of Content**

- [Install](#install)
    - [Automatic installation (recommended)](#automatic-installation-recommended)
    - [Manual installation](#manual-installation)
    - [Set up a Google API key](#set-up-a-google-api-key)
- [Management commands](#management-commands)
- [Tests](#tests)
- [Code Quality](#code-quality)
- [F.A.Q.](#faq)
- [Copyright & License](#copyright--license)

## Install

The API can be installed by following the recommended automatic installation
path, or manually if you need a more personal setup.

After having installed the application, complete your setup by following the
last steps describes in the [Set up a Google API key](#set-up-a-google-api-key)
section.

### Automatic installation (recommended)

#### Procedure

Use the procedure in the `dev-env`'s [README.md][dev-env-readme] to
automatically set up a fully functional environment with Docker.

### Manual installation

This method requires more efforts to set up the environment, as it implies
knowing how to: create a Python virtual environment; install and configure a
Django application; and how to install and configure a PostgreSQL server.

#### Required packages

- `python` >= 3.9
- `postgresql-13-server`
- `gettext` >= 0.21

#### Procedure

- Create a postgres
  database ([windows](https://www.postgresqltutorial.com/install-postgresql/),
  [macOS](https://www.postgresqltutorial.com/install-postgresql-macos/),
  [Linux](https://www.postgresqltutorial.com/install-postgresql-linux/)).

- Create a config file named `settings-tournesol.yaml`. You can find an
  [example](documentation/settings-tournesol.yaml) in documentation
  folder. You can put this file in different locations:
    - `/etc/tournesol/settings-tournesol.yaml` (linux),
    - Anywhere but add the `path/to/file` in SETTINGS_FILE environment
      variable,
    - Anywhere but add the `path/to/file` in SETTINGS_FILE variable `.env`
      file.
  
- Configure the settings according to their documentation to match your
  environment. For local developments you need to configure at least:
  - `CORS_ALLOWED_ORIGINS`
  - `DATABASE_NAME`, `DATABASE_USER` and `DATABASE_PASSWORD`
  - `MEDIA_ROOT` and `STATIC_ROOT`

- Create a python env and install the requirements
  `pip install -r requirements.txt`

- Create the database cache `python manage.py createcachetable`

- Install migrations on database `python manage.py migrate`

- Create superuser `python manage.py createsuperuser`

- Run the server `python manage.py runserver`

#### Install the development tools

The development tools contain the requirements to run the tests and the code
quality checks.

These tools are already included in the `dev-env`.

```shell
pip install -r tests/requirements.txt
```

### Set up a Google API Key

Configuring a Google API key allows the application to fetch video metadata
directly from YouTube. The application should still start without it, but some
features will be missing. It's recommended to get and configure this API key if
you plan to contribute regularly to the project, to make your environment
closer to the production one.

#### Requirements

1. a Google account
2. to be connected while following the procedure

#### Procedure

##### Create and configure the key

**(1)** First go to https://console.cloud.google.com/apis/ and create a new
project. You can choose the name you prefer, we suggest `tournesol`. You
should now be automatically redirected to the project dashboard.

**(2)** Go to the credentials page, accessible from the menu, and create new
`API key` credentials, without adding any restriction for now. The key will
be accessible from this screen by clicking on the key's name.

**(3)** Enable your API keys. As long as the keys are not activated, the
YouTube API will return an HTTP 403 error each time the back end will try to
get videos' metadata.

To activate your keys, you need to know your project id. You can copy it from
the URL parameter `?project=` or from the page
https://console.cloud.google.com/welcome.

Then simply visit the following URL. Don't forget to replace the string
`{YOUR_PROJECT_ID}` by your own project ID.

```
https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project={YOUR_PROJECT_ID}
```

##### Secure the key usage by adding restrictions

To secure the API key usage you need to add few restrictions.

Return to the page credentials of you project, and unfold the action menu of
your API key and click on modify.

In the modification page:

**(1)** Add an « application restriction » to define the only URLs or IP addresses
allowed to use the key (not relevant for local development environments).

**(2)** Also add an « API restriction » to make the key able to query only the
`YouTube Data API v3`. This setting can take few minutes to apply.

##### Configure the back end with the key

Finally, configure the `YOUTUBE_API_KEY` setting with the API key value in
your local `SETTINGS_FILE`. If you are using the `dev-env`, the settings file
is [backend/dev-env/settings-tournesol.yaml](./dev-env/settings-tournesol.yaml).

Restart the back end.

The back end is now ready to automatically update the videos' metadata when
new videos are added using the API, and when using the force refresh action.

## Management commands

`python manage.py create_dataset`

This command creates an up-to-date dataset archive on the disk.

It requires the setting `MEDIA_ROOT` to be configured with an absolute
filesystem path readable and writable by the user running the command.

```shell
# with a manually installed back end
python manage.py create_dataset

# with an automatically installed back end with Docker
docker exec tournesol-dev-api python manage.py create_dataset
```

`python manage.py watch_account_number`

This command checks if the number of accounts using a trusted email
domain exceeds predefined thresholds on a given date, and sends
alerts on Discord.

It takes 2 optional arguments:
- `-s` display the results only in the standard output (no alert sent)
- `-d date` check the accounts created on that date (format yyyy-mm-dd).

```shell
# By default -s is false and -d is today.
python manage.py watch_account_number

python manage.py watch_account_nulber -s -d 2020-01-31
```

## Tests

In order to ease your testing and debug time, use pytest : `pytest`
Moreover, you can run the following command to have a complete recap in a html
document for each test: `pytest --html=report.html --self-contained-html`

## Code Quality

We use several tools to keep the code quality as good, readable and
maintainable as possible:
- `isort` automatically sorts import statements
- `pylint` performs a static analysis looking for errors
- `flake8` enforces the code style by using three popular tools

All of them should be automatically triggered by the continuous integration
system using single script `scripts/ci/lint.sh`.

You are encouraged to run this script locally before creating a new commit.
Note that the script must be run from the root of the back end folder.

### Run the checks

```shell
# with a manually installed back end
./scripts/ci/lint.sh

# with an automatically installed back end with Docker
docker exec tournesol-dev-api scripts/ci/lint.sh
```

Files and folders can be passed as parameters.

```shell
# with a manually installed back end
./scripts/ci/lint.sh core/apps.py core/models/

# with an automatically installed back end with Docker
docker exec tournesol-dev-api scripts/ci/lint.sh core/apps.py core/models/
```

An output finishing by `+ exit 0` means all checks have been successful,
`+ exit 1` means at least one check has failed.

### Automatically fix some errors

Some tools, like `isort` are able to automatically fixes the target files.

```shell
# with a manually installed back end
./scripts/ci/lint-fix.sh

# with an automatically installed back end with Docker
docker exec tournesol-dev-api scripts/ci/lint-fix.sh
```

## F.A.Q.

**Why are the code quality tools not automatically triggered locally with the
help of the Git pre-commit hook?**

We try to use the [pre-commit][pre-commit] framework, but unfortunately it's
not adapted to work smoothly within our mono-repository
configuration [[faq-1][faq-1]].

Each time we found a solution a new issue appeared. In the end it requires much
more efforts to be configured and used rather than simply running the code
quality checks manually.

As we do not want to make the developers to have complex and error-prone local
setups, we decided to add the code quality checks only in the CI for now.

## Copyright & License

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

Included license:
 - [AGPL-3.0-or-later](./LICENSE)

[dev-env-readme]: https://github.com/tournesol-app/tournesol/blob/main/dev-env/README.md

[faq-1]: https://github.com/pre-commit/pre-commit/issues/466#issuecomment-531583187

[pre-commit]: https://pre-commit.com/
