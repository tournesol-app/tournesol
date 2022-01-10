# Tournesol Backend

The API of the Tournesol application, made with Python and Django.

## Install

### Automatic installation (recommended)

Use the procedure in the `dev-env`'s README.md to automatically set up a fully
functional environment with Docker.

### Manual installation

This method requires more efforts to set up the environment, as it implies
knowing how to: create a Python virtual environment; install and configure
a Django application; and how to install and configure a PostgreSQL server.

- Create a postgres database.

- Create a config file in /etc/django/settings-tournesol.yaml. You can find an example in documentation folder.

- You can set a different path with ENV variable SETTINGS_FILE.

- Create a python env and install the requirements
  `pip install -r requirements.txt`

- Install migrations on database `python manage.py migrate`

- Create the database cache `python manage.py createcachetable`

- Create superuser `python manage.py createsuperuser`

- Run the server `python manage.py runserver`

### Install the development tools

The development tools contain the requirements to run the tests and the code
quality checks.

If you have installed the back end with Docker, you will need to create a
virtual environment before running the following command.

First install the extra requirements in your virtual environment.

```python
pip install -r tests/requirements.txt
```

Then install the pre-commit hooks to trigger the code quality checks before
each commit.

```bash
pre-commit install
```

## Dependencies

Both `dev-env/run-docker-compose.sh` and `dev-env/run-db-and-local-django.sh` depend on [expect](https://core.tcl-lang.org/expect/index) for superuser unattended creation.

# Setup Google Api Key

* Go to https://console.cloud.google.com/apis/ and create a new project named `tournesol`

* Setup you credentials by getting a API key. Do not restrict its use for development purpose.

* Once you have created your API key, put it into `YOUTUBE_API_KEY` environment variable (`export YOUTUBE_API_KEY=xxx`)

* Then go to https://console.cloud.google.com/apis/credentials/consent, and add a user test (typicaly your gmail account)

# Testing

In order to ease your testing and debug time, use pytest : `pytest`
Moreover, you can run the following command to have a complete recap in a html document for each test:
`pytest --html=report.html --self-contained-html`

# Code Quality

We use several tools to keep the code quality as good, readable and maintainable
as possible:
- `isort` automatically sorts import statements
- `pylint` static code analyzer which looks for errors
- `flake8` a wrapper around three popular tools for style enforcement

All of them will be automatically triggered as pre-commit hooks if you
installed the development dependencies from `tests/requirements.txt.`
