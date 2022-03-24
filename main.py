"""
A bot that occasionally tweets a random Wikipedia page.

Twitter | {to be added}
"""

from twitter_api import *
import requests
from bs4 import BeautifulSoup as bs
import json
import schedule

CREDENTIALS = json.load(open("credentials.json"))
page_url = "https://en.wikipedia.org/wiki/Special:Random"

twitter = Twitter(
    access_token=CREDENTIALS["access_token"],
    user_access_secret=CREDENTIALS["user_access_secret"],
    oauth_consumer_key=CREDENTIALS["oauth_consumer_key"],
    consumer_secret=CREDENTIALS["consumer_secret"]
)


def tweet_article():
    page = requests.get(page_url)
    soup = bs(page.text, features="html.parser")
    page_name = soup.find("h1", {"id": "firstHeading"}).get_text()

    info = soup.find_all("p", {"class": ""})

    # the intro paragraph does not have a class name or other identifier, however therer are a bunch of other p tags
    # that don't have an identifier either. This is meant to only get the text we care about (the intro)
    scraped = None
    for i in info:
        tag = i.find_parent()
        if tag.name == "div":
            if 'class' in tag.attrs and "mw-parser-output" in tag['class']:
                header_len = 280 - len(f"{page_url} - ...")
                scraped = f"{page_name} - {i.get_text()[0:header_len]}..."
                t = twitter.Tweet()
                t.text(scraped)
                return t.send_as_oauth1()

schedule.every().day.at("12:00").do(tweet_article())