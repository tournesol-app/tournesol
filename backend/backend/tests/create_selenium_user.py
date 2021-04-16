from django_react.selenium_config import SELENIUM_USERNAME, SELENIUM_PASSWORD
from backend.models import DjangoUser


def create_selenium_user():
    """Create Selenium user account."""
    DjangoUser.objects.filter(username=SELENIUM_USERNAME).delete()
    DjangoUser.objects.create_user(
        username=SELENIUM_USERNAME,
        password=SELENIUM_PASSWORD,
        email="admin@example.com",
        is_active=True,
        is_superuser=False)
