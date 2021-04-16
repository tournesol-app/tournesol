from django.core.management.base import BaseCommand
import secrets
from coolname import generate_slug
from backend.models import DjangoUser, UserInformation, VerifiableEmail
from backend.reset_password import reset_password
from django_react.settings import EMAIL_PAGE_DOMAIN
import pandas as pd
from datetime import datetime


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--num_accounts', help='Number of accounts to create', type=int,
                            default=1)

    def handle(self, **options):
        accounts = []

        n = options['num_accounts']

        for i in range(n):
            print(f"=== Creating account {i + 1}...")

            username = generate_slug(2) + "-" + secrets.token_urlsafe(4)
            password = secrets.token_urlsafe(15)
            email = f"{username}@tournesol.app"

            u = DjangoUser.objects.create_user(username=username,
                                               password=password,
                                               email=email)
            ui = UserInformation.objects.create(user=u, is_demo=True)
            email = VerifiableEmail.objects.create(
                email=email, user=ui, is_verified=True)

            token = reset_password(username, do_send_mail=False)

            link = f"{EMAIL_PAGE_DOMAIN}welcome/?token={token}"

            accounts.append({
                'username': username,
                'password': password,
                'email': email,
                'token': token,
                'link': link,
            })

            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"E-mail: {email}")
            print(f"Token: {token}")
            print(f"Link: {link}")

        df = pd.DataFrame(accounts)
        dt = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = f'demo_accounts-{n}-{dt}.csv'
        df.to_csv(fn, index=False)

        print(f"List of accounts written to {fn}")
