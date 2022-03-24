"""
A bot that occasionally tweets a random Wikipedia page.

Twitter | {to be added}
"""

from twitter_api import *
import requests
from bs4 import BeautifulSoup as bs
import json
import schedule
import sys

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
    for i in info:
        tag = i.find_parent()
        if tag.name == "div":
            if 'class' in tag.attrs and "mw-parser-output" in tag['class']:
                max_content_len = 280 - len(f"{page_name} - ")
                ellipsis = ""

                if len(i.get_text()) > max_content_len:
                    max_content_len -= 3 # account for elipses
                    ellipsis = "..."

                scraped = f"{page_name} - {i.get_text()[0:max_content_len]}{ellipsis}"
                t = twitter.Tweet()
                t.text(scraped)
                print(f"sending the following to twitter:\n{scraped}")
                return t.send_as_oauth1()

if len(sys.argv) == 2 and sys.argv[1] == "daily":
    print("\x1b[31m**DAILY RUN**\x1b[0m")
    schedule.every().day.at("12:00").do(tweet_article)
else:
    print("\x1b[31m**HOURLY RUN**\x1b[0m")
    schedule.every().hour.do(tweet_article)

print("setup complete, listening...")
while True:
    schedule.run_pending()