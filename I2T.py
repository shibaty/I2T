#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Instagram to Twitter """

import os
import sys
import urllib
import time
from datetime import datetime

import config
from InstagramClient import InstagramClient
from TwitterClient import TwitterClient

INTERVAL = config.CONFIG['INTERVAL_SECONDS']
FILEPATH = "/tmp/Instagram/"

def download_medias(urls):
    """donload medias"""
    paths = []
    for url in urls:
        path = urllib.request.urlretrieve(url)
        paths.append(path[0])
    return paths

def cleanup_medias():
    """cleanup downloaded medias"""
    urllib.request.urlcleanup()

def get_instagram_recent_post():
    """get Instagram recent post"""

    insta = InstagramClient(config.CONFIG['INSTAGRAM_ACCESS_TOKEN'],
                            config.CONFIG['INSTAGRAM_CLIENT_SECRET'])

    media = insta.get_recent_media()

    created_time = media.get_created_time()
    now_time = datetime.utcnow()
    delta = now_time - created_time

    if delta.total_seconds() >= INTERVAL:
        return False, "", "", []

    caption = media.get_caption()
    link = media.get_link()
    urls = media.get_media_urls()

    return True, caption, link, urls

def post_twitter(caption, link, paths):
    """post twitter"""
    twit = TwitterClient(config.CONFIG['TWITTER_CONSUMER_KEY'],
                         config.CONFIG['TWITTER_CONSUMER_SECRET'],
                         config.CONFIG['TWITTER_ACCESS_TOKEN_KEY'],
                         config.CONFIG['TWITTER_ACCESS_TOKEN_SECRET'])

    #message = u"{0} {1}".format(caption, link)
    #if len(message) > 140:
    #    message = caption
    message = caption
    message = message[0:140]
    twit.post_with_medias(message, paths)

def main_routine():
    """main routine"""

    while True:
        try:
            ret, caption, link, urls = get_instagram_recent_post()
            if ret:
                paths = download_medias(urls)
                post_twitter(caption, link, paths)
                cleanup_medias()
        except IOError:
            print("Network unreachable?")

        print("sleeping {0} seconds...".format(INTERVAL))
        time.sleep(INTERVAL)

def fork():
    """fork"""
    pid = os.fork()

    if pid > 0:
        pid_file = open("/var/run/I2T.pid", 'w')
        pid_file.write(str(pid) + "\n")
        pid_file.close()
        sys.exit()

    if pid == 0:
        main_routine()

# main
if __name__ == '__main__':
    fork()
