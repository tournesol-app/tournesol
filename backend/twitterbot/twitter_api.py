import tweepy
from django.conf import settings

CREDENTIALS = settings.TWITTERBOT_CREDENTIALS


class TwitterBot:
    def __init__(self, account):

        if account not in CREDENTIALS:
            raise ValueError(f"No credentials found for {account} account!")

        account_cred = CREDENTIALS[account]

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
