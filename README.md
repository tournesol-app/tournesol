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
