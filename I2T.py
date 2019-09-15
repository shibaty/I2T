#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Instagram to Twitter """

import os
import sys
import urllib.request
import shutil
import time
from datetime import datetime

import config
from InstagramClient import InstagramClient
from TwitterClient import TwitterClient

INTERVAL = config.CONFIG['INTERVAL_SECONDS']
DOWNLOAD_FILE_PATH = '/tmp/'


def download_medias(urls):
    """donload medias"""
    paths = []
    for count, url in enumerate(urls):
        if count >= config.CONFIG['TWITTER_MEDIAS_MAX']:
            break
        filename = url.rsplit('/', 1)[1].split('?')[0]
        path = DOWNLOAD_FILE_PATH + filename
        with urllib.request.urlopen(url) as data, open(path, 'wb') as file:
            shutil.copyfileobj(data, file)
        paths.append(path)
    return paths


def cleanup_medias(paths):
    """cleanup downloaded medias"""
    for path in paths:
        os.remove(path)


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

    media_ids = []
    media_video_ids = []
    for path in paths:
        _, ext = os.path.splitext(path)
        if ext == '.mp4':
            media_video_ids.append(twit.media_upload_video(path))
        else:
            media_ids.append(twit.media_upload(path))

    media_ids_len = len(media_ids)
    media_video_ids_len = len(media_video_ids)
    count = 1
    count_max = 0
    count_message = ""

    if media_ids_len > 0:
        if media_video_ids_len > 0:
            count_max = media_ids_len + media_video_ids_len
            count_message = str(count) + "/" + str(count_max) + " "
            count = count + 1
        message = (count_message + caption)[0:140]
        twit.post_with_medias(message, media_ids)

    for media_video_id in media_video_ids:
        if count_max > 1:
            count_message = str(count) + "/" + str(count_max) + " "
        message = (count_message + caption)[0:140]
        twit.post_with_medias(message, {media_video_id})
        count = count + 1

def get_and_post():
    """get instagram recent post and post twitter"""
    try:
        ret, caption, link, urls = get_instagram_recent_post()
        if ret:
            paths = download_medias(urls)
            post_twitter(caption, link, paths)
            cleanup_medias(paths)
    except IOError:
        print("Network unreachable?")

def main_routine():
    """main routine"""

    while True:
        get_and_post()

        time.sleep(INTERVAL)

# main
if __name__ == '__main__':
    main_routine()

