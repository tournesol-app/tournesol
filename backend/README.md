# Tournesol Backend

The API of the Tournesol application, made with Python and Django.

## Install

### Automatic installation (recommended)

Use the procedure in the `dev-env`'s [README.md][dev-env-readme] to
automatically set up a fully functional environment with Docker.

### Manual installation

This method requires more efforts to set up the environment, as it implies
knowing how to: create a Python virtual environment; install and configure
a Django application; and how to install and configure a PostgreSQL server.

#### Required packages

- `python` >= 3.9
- `postgresql-13-server`
- `gettext` >= 0.21

#### Procedure

- Create a postgres database.

- Create a config file in /etc/django/settings-tournesol.yaml. You can find an example in documentation folder.

- You can set a different path with ENV variable SETTINGS_FILE.

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

```python
pip install -r tests/requirements.txt
```

## Dependencies

Both `dev-env/run-docker-compose.sh` and `dev-env/run-db-and-local-django.sh` depend on [expect](https://core.tcl-lang.org/expect/index) for superuser unattended creation.

## Setup Google Api Key

* Go to https://console.cloud.google.com/apis/ and create a new project named `tournesol`

* Setup you credentials by getting a API key. Do not restrict its use for development purpose.

* Set `YOUTUBE_API_KEY` value in your `SETTINGS_FILE`.  
If you are using the "dev-env", this is in [backend/dev-env/settings-tournesol.yaml](./dev-env/settings-tournesol.yaml)

* Then go to https://console.cloud.google.com/apis/credentials/consent, and add a user test (typicaly your gmail account)

## Testing

In order to ease your testing and debug time, use pytest : `pytest`
Moreover, you can run the following command to have a complete recap in a html document for each test:
`pytest --html=report.html --self-contained-html`

## Code Quality

We use several tools to keep the code quality as good, readable and maintainable
as possible:
- `isort` automatically sorts import statements
- `pylint` performs a static analysis looking for errors
- `flake8` enforces the code style by using three popular tools

All of them should be automatically triggered by the continuous integration
system using single script `scripts/ci/lint.sh`.

You are encouraged to run this script locally before creating a new commit.
Note that the script must be run from the root of the back end folder. 

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

## F.A.Q.

**Why are the code quality tools not automatically triggered locally with
the help of the Git pre-commit hook?**

We try to use the [pre-commit][pre-commit] framework, but unfortunately it's
not adapted to work smoothly within our mono-repository
configuration [[faq-1][faq-1]].

Each time we found a solution a new issue appeared. In the end it requires
much more efforts to be configured and used rather than simply running the
code quality checks manually.

As we do not want to make the developers to have complex and error-prone local
setups, we decided to add the code quality checks only in the CI for now.

[dev-env-readme]: https://github.com/tournesol-app/tournesol/blob/main/dev-env/README.md

[faq-1]: https://github.com/pre-commit/pre-commit/issues/466#issuecomment-531583187

[pre-commit]: https://pre-commit.com/
