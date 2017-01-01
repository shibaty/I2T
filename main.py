#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import time
from datetime import datetime

import config
from InstagramClient import InstagramClient
from TwitterClient import TwitterClient

interval = config.CONFIG["INTERVAL_SECONDS"]
caption = ""
link = ""
filepath = "/tmp/InstaTemp.jpg"

def downloadImage(url, filepath):
    urllib.urlretrieve(url, filepath)

def getInstagramRecentPost():
    global caption
    global link

    insta = InstagramClient(
        config.CONFIG["INSTAGRAM_ACCESS_TOKEN"],
        config.CONFIG["INSTAGRAM_CLIENT_SECRET"])

    media = insta.getRecentMedia()

    caption = media.getCaption()
    link = media.getLink()
    imageUrl = media.getImageUrl()

    downloadImage(imageUrl, filepath)

    createdTime = media.getCreatedTime()
    nowTime = datetime.utcnow()
    delta = nowTime - createdTime 

    if delta.total_seconds() < interval:
        return True

    return False

def postTwitter():
    global caption
    global link

    twit = TwitterClient(
        config.CONFIG["TWITTER_CONSUMER_KEY"],
        config.CONFIG["TWITTER_CONSUMER_SECRET"],
        config.CONFIG["TWITTER_ACCESS_TOKEN_KEY"],
        config.CONFIG["TWITTER_ACCESS_TOKEN_SECRET"])

    message = u"{0} {1}".format(caption, link)
    twit.postWithMedia(message, filepath)

# main 

while True:

    if getInstagramRecentPost():
        print "post."
        postTwitter()

    time.sleep(interval)

