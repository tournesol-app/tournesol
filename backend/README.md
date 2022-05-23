# Tournesol back end

The API of the Tournesol platform, made with Python and Django.

**Table of Content**

- [Install](#install)
    - [Automatic installation (recommended)](#automatic-installation-recommended)
    - [Manual installation](#manual-installation-advanced)
    - [Set up a Google API key](#set-up-a-google-api-key)
- [Tests](#tests)
- [Code Quality](#code-quality)
- [F.A.Q.](#faq)

## Install

The API can be installed by following the recommended automatic installation
path, or manually if you need a more personal setup.

After having installed the application, complete your setup by following the
last steps describes in the [Set up a Google API key](#set-up-a-google-api-key)
section.

### Automatic installation (recommended)

#### Required packages

- [expect](https://core.tcl-lang.org/expect/index)

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
  [example](backend/documentation/settings-tournesol.yaml) in documentation
  folder. You can put this file in different locations:
    - `/etc/tournesol/settings-tournesol.yaml` (linux),
    - Anywhere but add the `path/to/file` in SETTINGS_FILE environment
      variable,
    - Anywhere but add the `path/to/file` in SETTINGS_FILE variable `.env`
      file.

- Create a python env and install the requirements
  `pip install -r requirements.txt`

- Install migrations on database `python manage.py migrate`

- Create the database cache `python manage.py createcachetable`

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
3. to have at least one YouTube video in the database

#### Procedure

##### Create and configure the key

**(1)** Go to https://console.cloud.google.com/apis/ and create a new project. You
can choose the name you prefer, we suggest `tournesol`. You should now
be automatically redirected to the project dashboard.

**(2)** Go to the credentials page, accessible from the menu, and create new
`API key `credentials. You should now be able to see the API key value by
clicking on it.

**(3)** Unfold the action menu of your API key and click on modify. To secure
the key usage you need to add few restrictions.

Add an application restriction to define the only URLs or IP addresses allowed
to use the key (not relevant for local development environments).

Also add an API restriction to make the key able to query only the
`YouTube Data API v3`. This setting can take few minutes to apply.

##### Configure the back end

Now configure the `YOUTUBE_API_KEY` setting with the API key value in your
`SETTINGS_FILE`.  If you are using the dev-env, the settings file is
[backend/dev-env/settings-tournesol.yaml](./dev-env/settings-tournesol.yaml)

Finally, you need to enable your API key. The first time the back end will try
to get metadata from YouTube, you will see an HTTP 403 error in the back end's
logs, with an activation link.

- Start the back end
- Log in the administration interface with your superuser
- Go the entities list
- Select a YouTube video entity and run the action force refresh metadata 

Check the back end's logs, and copy and paste the activation link in you
browser. The link should look like this:

```
https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=[YOUR_PROJECT_ID]
```

The back end is now ready to automatically update the videos' metadata when
new videos are added using the API, and when using the force refresh action.

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

[dev-env-readme]: https://github.com/tournesol-app/tournesol/blob/main/dev-env/README.md

[faq-1]: https://github.com/pre-commit/pre-commit/issues/466#issuecomment-531583187

[pre-commit]: https://pre-commit.com/
