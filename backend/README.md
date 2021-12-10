# Tournesol Backend

Django app for tournesol app.

# Installation

- Create a postgres database.

- Create a config file in /etc/django/settings-tournesol.yaml. You can find an example in documentation folder.

- You can set a different path with ENV variable SETTINGS_FILE.

- Create a python env and install the requirements
  `pip install -r requirements.txt`

- Install migrations on database
  `python manage.py migrate`

- Create superuser
  `python manage.py createsuperuser`

- Run the server
  `python manage.py runserver`

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
