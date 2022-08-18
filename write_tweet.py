import os
import tweepy


def twitter_authentication():
    auth = tweepy.OAuthHandler(
        os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"]
    )
    auth.set_access_token(os.environ["ACCESS_TOKEN"], os.environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def tweet(api):
    api.update_status("Still not done")


if __name__ == "__main__":
    api = twitter_authentication()
    tweet(api)
