Tournesol Backend
===

Django app for tournesol app.


# Installation

* Create a postgres database.


* Create a config file in /etc/django/settings-tournesol.yaml. You can find an example in documentation folder.


* You can set a different path with ENV variable SETTINGS_FILE.


* Create a python env and install the requirements
``pip install -r requirements.txt``


* Install migrations on database
``python manage.py migrate``
  

* Create superuser
``python manage.py createsuperuser``


* Run the server
``python manage.py runserver``