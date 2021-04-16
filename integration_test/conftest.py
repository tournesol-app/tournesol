import pytest
from helpers import get_driver, close_driver, SELENIUM_USERNAME
from django_react.settings import DATABASES_AVAILABLE
from backend.models import DjangoUser
from django.db import connection
import logging
from django.apps import apps


@pytest.fixture(scope='session', autouse=True)
def driver():
    """Create the driver."""

    driver = get_driver()

    yield driver

    close_driver(driver)


@pytest.fixture(scope='session')
def django_db_setup():
    from django.conf import settings
    settings.DATABASES['default'] = DATABASES_AVAILABLE['sqlite']


@pytest.fixture(autouse=True)
def clear_data(django_db_blocker):
    logging.info("Reconnecting to database")
    with django_db_blocker.unblock():
        connection.connect()
    logging.info("Cleaning all data...")
    with django_db_blocker.unblock():
        DjangoUser.objects.exclude(username=SELENIUM_USERNAME).delete()
        for model in apps.get_models():
            if model.__module__ == 'backend.models':
                model.objects.all().delete()


@pytest.fixture(autouse=True)
def clear_cookies(driver):
    logging.info("Clearing cookies")
    driver.delete_all_cookies()
