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

* Once you have created your API key, put it into `YOUTUBE_API_KEY` environment variable (`export YOUTUBE_API_KEY=xxx`)

* Then go to https://console.cloud.google.com/apis/credentials/consent, and add a user test (typicaly your gmail account)

## Testing

In order to ease your testing and debug time, use pytest : `pytest`
Moreover, you can run the following command to have a complete recap in a html document for each test:
`pytest --html=report.html --self-contained-html`

## Code Quality

We use several tools to keep the code quality as good, readable and maintainable
as possible:
- `isort` automatically sorts import statements
- `pylint` static code analyzer which looks for errors
- `flake8` a wrapper around three popular tools for style enforcement

All of them should be automatically triggered by the continuous
integration system.

You can run them locally before creating a new commit, by running the
following commands.

**manual installation**

The commands should be run from the root of the Git repository. 

```shell
# check file by file
isort file1.py file2.py
pylint --rcfile=backend/.pylintrc file1.py file2.py
flake8 --config=backend/.flake8 file1.py file2.py

# check the whole git index (i.e. all files added with git add)
git diff --name-only --cached | xargs -r isort
git diff --name-only --cached | xargs -r pylint --rcfile=backend/.pylintrc
git diff --name-only --cached | xargs -r flake8 --config=backend/.flake8 
```

**automatic installtion with Docker**

The commands should be run from the backend sub-folder.

```shell
docker exec tournesol-dev-api isort file1.py file2.py
docker exec tournesol-dev-api pylint --rcfile=.pylintrc file1.py file2.py
docker exec tournesol-dev-api flake8 --config=.flake8 file1.py file2.py
```

## F.A.Q.

**Why are the code quality tools not automatically triggered locally with
the help of the Git pre-commit hook?**

We try to use the [pre-commit][pre-commit] framework, but unfortunately it's
not adapted to work smoothly within our mono-repository
configuration [[faq-1]][faq-1].

Each time we found a solution a new issue appeared. In the end it requires
much more efforts to be configured and used rather than simply running the
code quality checks manually.

As we do not want to make the developers to have complex and error-prone local
setups, we decided to add the code quality checks only in the CI for now.

[dev-env-readme]: https://github.com/tournesol-app/tournesol/blob/main/dev-env/README.md

[faq-1]: https://github.com/pre-commit/pre-commit/issues/466#issuecomment-531583187

[pre-commit]: https://pre-commit.com/
