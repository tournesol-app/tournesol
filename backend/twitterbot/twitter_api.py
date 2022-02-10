import tweepy
from credentials import secrets


class TwitterBot:
    def __init__(self, account):

        if not account in secrets.keys():
            raise ValueError(f"No credentials found for {account} account!")

        self.language = secrets[account]["LANGUAGE"]
        self.consumer_key = secrets[account]["CONSUMER_KEY"]
        self.consumer_secret = secrets[account]["CONSUMER_SECRET"]
        self.access_token = secrets[account]["ACCESS_TOKEN"]
        self.access_token_secret = secrets[account]["ACCESS_TOKEN_SECRET"]

    def authenticate(self):

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        self.api = tweepy.API(auth)

        if self.api.verify_credentials():
            print("Twitter authentication OK")
        else:
            raise ConnectionError("Error during Twitter authentication")
