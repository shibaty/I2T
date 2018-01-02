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
    for url in urls:
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
    # for debug print
    print(link)

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

    message = caption

    media_ids_len = len(media_ids)
    media_video_ids_len = len(media_video_ids)
    count = 1
    count_max = 0

    if media_ids_len > 0:
        if media_video_ids_len > 0:
            count_max = media_ids_len + media_video_ids_len
            message = str(count) + "/" + str(count_max) + " " + message
            count = count + 1
        message = message[0:140]
        twit.post_with_medias(message, media_ids)

    for media_video_id in media_video_ids:
        message = str(count) + "/" + str(count_max) + " " + caption
        message = message[0:140]
        twit.post_with_medias(message, {media_video_id})
        count = count + 1


def main_routine():
    """main routine"""

    while True:
        try:
            ret, caption, link, urls = get_instagram_recent_post()
            if ret:
                paths = download_medias(urls)
                post_twitter(caption, link, paths)
                cleanup_medias(paths)
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
