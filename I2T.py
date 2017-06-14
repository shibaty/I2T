#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Instagram to Twitter """

import os
import sys
import urllib
import time
from datetime import datetime
import httplib2

import config
from InstagramClient import InstagramClient
from TwitterClient import TwitterClient

INTERVAL = config.CONFIG["INTERVAL_SECONDS"]
caption = " "
link = " "
FILEPATH = "/tmp/InstaTemp.jpg"

def download_image(url):
    """donload image"""
    urllib.urlretrieve(url, FILEPATH)

def get_instagram_recent_post():
    """get Instagram recent post"""
    global caption
    global link

    insta = InstagramClient(config.CONFIG["INSTAGRAM_ACCESS_TOKEN"],
                            config.CONFIG["INSTAGRAM_CLIENT_SECRET"])

    media = insta.get_recent_media()

    created_time = media.get_created_time()
    now_time = datetime.utcnow()
    delta = now_time - created_time

    if delta.total_seconds() >= INTERVAL:
        return False

    caption = media.get_caption()
    link = media.get_link()
    image_url = media.get_image_url()

    download_image(image_url)

    return True

def post_twitter():
    """post twitter"""
    twit = TwitterClient(config.CONFIG["TWITTER_CONSUMER_KEY"],
                         config.CONFIG["TWITTER_CONSUMER_SECRET"],
                         config.CONFIG["TWITTER_ACCESS_TOKEN_KEY"],
                         config.CONFIG["TWITTER_ACCESS_TOKEN_SECRET"])

    message = u"{0} {1}".format(caption, link)
    twit.post_with_media(message, FILEPATH)

def main_routine():
    """main routine"""
    while True:
        try:
            if get_instagram_recent_post():
                post_twitter()
        except httplib2.ServerNotFoundError:
            print "Network is unavailable?"

        print "sleeping {0} seconds...".format(INTERVAL)
        time.sleep(INTERVAL)

def fork():
    """fork"""
    pid = os.fork()

    if pid > 0:
        pid_file = open('/var/run/I2T.pid', 'w')
        pid_file.write(str(pid) + "\n")
        pid_file.close()
        sys.exit()

    if pid == 0:
        main_routine()

# main
if __name__ == '__main__':
    fork()
