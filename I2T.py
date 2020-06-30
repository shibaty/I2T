# -*- coding: utf-8 -*-
""" Instagram to Twitter """

import os
import urllib.request
import shutil
import time
import mimetypes
from datetime import datetime, timezone

from settings.Settings import Settings
from clients.InstagramClient import InstagramClient
from clients.TwitterClient import TwitterClient

DOWNLOAD_FILE_PATH = '/tmp/'


def download_medias(urls):
  """donload medias"""
  paths = []
  settings = Settings.get_instance()
  medias_max = int(settings.get_config('TWITTER_MEDIAS_MAX'))
  for count, url in enumerate(urls):
    if count >= medias_max:
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


def get_instagram_recent_post(interval):
  """get Instagram recent post"""

  settings = Settings.get_instance()
  insta = InstagramClient(settings.get_config('INSTAGRAM_ACCESS_TOKEN'))

  media = insta.get_recent_media()

  created_time = media.get_timestamp()
  now_time = datetime.now(timezone.utc)
  delta = now_time - created_time

  if int(delta.total_seconds()) >= interval + 10:
    return False, '', []

  caption = media.get_caption()
  urls = media.get_media_urls()

  print('get instagram Caption: ' + caption)

  return True, caption, urls


def post_twitter(caption, paths):
  """post twitter"""

  print("post twitter Caption: " + caption)

  settings = Settings.get_instance()
  config = settings.get_config_all()
  twit = TwitterClient(config['TWITTER_CONSUMER_KEY'],
                       config['TWITTER_CONSUMER_SECRET'],
                       config['TWITTER_ACCESS_TOKEN_KEY'],
                       config['TWITTER_ACCESS_TOKEN_SECRET'])

  media_ids = []
  media_videos_count = 0
  for path in paths:
    mime_type = mimetypes.guess_type(path)[0]
    if 'video' in mime_type:
      media_videos_count = media_videos_count + 1
    else:
      media_ids.append(twit.media_upload(path, mime_type))

  media_ids_len = len(media_ids)
  count = 1
  count_max = 0
  count_message = ""

  if media_ids_len > 0:
    if media_videos_count > 0:
      count_max = 1 + media_videos_count
      count_message = str(count) + "/" + str(count_max) + " "
      count = count + 1
    message = (count_message + caption)[0:140]
    twit.post_with_medias(message, media_ids)

  for path in paths:
    mime_type = mimetypes.guess_type(path)[0]
    if 'video' in mime_type:
      count_message = str(count) + "/" + str(count_max) + " "
      message = (count_message + caption)[0:140]
      media_video_id = twit.media_upload(path, mime_type)
      twit.post_with_medias(message, {media_video_id})
      count = count + 1


def get_and_post(interval):
  """get instagram recent post and post twitter"""
  try:
    ret, caption, urls = get_instagram_recent_post(interval)
    if ret:
      paths = download_medias(urls)
      post_twitter(caption, paths)
      cleanup_medias(paths)
  except IOError:
    print('Network unreachable?')


def main_routine():
  """main routine"""
  settings = Settings.get_instance()
  interval = int(settings.get_config('INTERVAL_SECONDS'))

  print('I2T INTERVAL:' + str(interval) + ' secs')
  while True:
    get_and_post(interval)
    time.sleep(interval)


# main
if __name__ == '__main__':
  main_routine()
