from django.core.management.base import BaseCommand
from backend.tests.create_selenium_user import create_selenium_user
from django_react.selenium_config import SELENIUM_USERNAME, SELENIUM_PASSWORD
from frontend.views import create_user_preferences


class Command(BaseCommand):
    def handle(self, **options):
        create_selenium_user()
        create_user_preferences()
        print(f"{SELENIUM_USERNAME}:{SELENIUM_PASSWORD}")
