import os
import tweepy
import datetime
import numpy as np
import pandas as pd

from github import Github
from zoneinfo import ZoneInfo
from json_tricks import load, dump


def get_secrets(local_secrets_path=None):
    if local_secrets_path is None:
        local_secrets_path = os.path.join("local_secrets", "secrets.json")
    if os.path.isfile(local_secrets_path):
        with open(local_secrets_path, "r") as json_file:
            secrets = load(json_file)
    else:
        secrets = os.environ
    return secrets


def github_repo_authentication(secrets=os.environ):
    access_token = secrets["ACCESS_TOKEN_GITHUB"]
    repo_path = secrets["REPO_PATH_GITHUB"]
    g = Github(access_token)
    return g.get_repo(repo_path)


def get_stats_yesterday(stats_df_path="stats.csv", secrets=os.environ):
    repo = github_repo_authentication(secrets=secrets)
    contents = repo.get_contents("stats.csv")
    download_url = contents._download_url.value
    stats_df = pd.read_csv(download_url)
    yesterday = get_datetime_yesterday()
    can_format = "%Y-%m-%d"
    yesterday_str = yesterday.strftime(can_format)
    stats_df["date"] = [datetime.datetime.fromisoformat(dt).strftime(
        can_format) for dt in stats_df["datetime"].values]
    return stats_df[stats_df["date"] == yesterday_str]


def get_datetime_yesterday(orig_tz_str="UTC", local_tz_str="America/Montreal", use_local_tz=True):
    if use_local_tz:
        tz = ZoneInfo(local_tz_str)
    else:
        tz = ZoneInfo(orig_tz_str)
    now = datetime.datetime.now(tz=tz)
    return now - datetime.timedelta(days=1)


def twitter_authentication(secrets=os.environ):
    auth = tweepy.OAuthHandler(
        secrets["CONSUMER_KEY"], secrets["CONSUMER_SECRET"]
    )
    auth.set_access_token(secrets["ACCESS_TOKEN"],
                          secrets["ACCESS_TOKEN_SECRET"])
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

    secrets = get_secrets()

    stats_yesterday = get_stats_yesterday(secrets=secrets)
    sums_yesterday = stats_yesterday.sum()
    stats_str = ("updates " + str(stats_yesterday["date"].values[0]) + ": " +
                 str(sums_yesterday["changes"]) + " lines changed (" +
                 str(sums_yesterday["additions"]) + " additions, " +
                 str(sums_yesterday["deletions"]) + " deletions) ")

    json_path = "tweet_info.json"
    hashtag = update_hashtag(json_path)
    status = "Still not done..." + stats_str + "#" + hashtag

    api = twitter_authentication(secrets=secrets)

    tweet(api, status=status)
