import tweepy
from django.conf import settings


class TwitterBot:
    def __init__(self, account):

        credentials = settings.TWITTERBOT_CREDENTIALS

        if account not in credentials:
            raise ValueError(f"No credentials found for {account} account!")

        account_cred = credentials[account]

        self.language = account_cred["LANGUAGE"]
        self.consumer_key = account_cred["CONSUMER_KEY"]
        self.consumer_secret = account_cred["CONSUMER_SECRET"]
        self.access_token = account_cred["ACCESS_TOKEN"]
        self.access_token_secret = account_cred["ACCESS_TOKEN_SECRET"]
        self.api = None

    def authenticate(self):

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        self.api = tweepy.API(auth)

        if self.api.verify_credentials():
            print("Twitter authentication OK")
        else:
            raise ConnectionError("Error during Twitter authentication")
