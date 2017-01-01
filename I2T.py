#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
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

    createdTime = media.getCreatedTime()
    nowTime = datetime.utcnow()
    delta = nowTime - createdTime 

    if delta.total_seconds() >= interval:
        return False

    caption = media.getCaption()
    link = media.getLink()
    imageUrl = media.getImageUrl()

    downloadImage(imageUrl, filepath)

    return True

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
def mainRoutine():
    while True:

        if getInstagramRecentPost():
            "post to Twitter from Intagram Recent Media."
            postTwitter()

        print "sleeping {0} seconds...".format(interval)
        time.sleep(interval)

def fork():
    pid = os.fork()

    if pid > 0:
        f = open('/var/run/I2T.pid','w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()

    if pid == 0:
        mainRoutine()

if __name__=='__main__': 
    fork()
