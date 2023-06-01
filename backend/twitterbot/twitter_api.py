import tweepy
from django.conf import settings


class TwitterBot:
    def __init__(self, account):

        credentials = settings.TWITTERBOT_CREDENTIALS

        if account not in credentials:
            raise ValueError(f"No credentials found for {account} account!")

        account_cred = credentials[account]

        self.language = account_cred["LANGUAGE"]

        consumer_key = account_cred["CONSUMER_KEY"]
        consumer_secret = account_cred["CONSUMER_SECRET"]
        access_token = account_cred["ACCESS_TOKEN"]
        access_token_secret = account_cred["ACCESS_TOKEN_SECRET"]

        # v2
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        # v1.1
        # We need this authentication also because to add media it only works with api v1.1
        auth = tweepy.OAuth1UserHandler(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        self.api = tweepy.API(auth)
