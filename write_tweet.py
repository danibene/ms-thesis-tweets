import os
import tweepy
import numpy as np

from json_tricks import load, dump


def twitter_authentication():
    auth = tweepy.OAuthHandler(
        os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"]
    )
    auth.set_access_token(os.environ["ACCESS_TOKEN"], os.environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def tweet(api, status="Still not done"):
    api.update_status(status)


def get_new_hashtag(d):
    hashtag = d["last_hashtag_tweeted"]
    while hashtag == d["last_hashtag_tweeted"]:
        hashtag_index = np.random.randint(0, high=len(d["hashtags"]))
        hashtag = d["hashtags"][hashtag_index]
    return hashtag


def update_hashtag(json_path):
    with open(json_path, "r") as json_file:
        d = load(json_file)

    hashtag = get_new_hashtag(d)
    d["last_hashtag_tweeted"] = hashtag

    with open(json_path, "w") as json_file:
        dump(d, json_file)

    return hashtag


if __name__ == "__main__":
    api = twitter_authentication()
    json_path = "tweet_info.json"
    hashtag = update_hashtag(json_path)
    status = "Still not done #" + hashtag
    tweet(api, status=status)
