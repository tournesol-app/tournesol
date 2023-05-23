import tweepy
from django.conf import settings


class TwitterBot:
    def __init__(self, account):

        credentials = settings.TWITTERBOT_CREDENTIALS

        if account not in credentials:
            raise ValueError(f"No credentials found for {account} account!")

        account_cred = credentials[account]

        self.language = account_cred["LANGUAGE"]
        self.bearer_token = account_cred["ACCESS_TOKEN"]

        # v2
        self.client = tweepy.Client(self.bearer_token)

        # v1.1
        # We need this authentication also because to add media it only works with api v1.1
        auth = tweepy.OAuth2BearerHandler(self.bearer_token)
        self.api = tweepy.API(auth)
