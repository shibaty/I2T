# -*- coding: utf-8 -*-
""" Instagram to Twitter """

import os
import schedule
import urllib.request
import shutil
import time
import mimetypes
from datetime import datetime, timezone

from settings.Settings import Settings
from clients.InstagramClient import InstagramClient
from clients.TwitterClient import TwitterClient
from utils.Logger import Logger

DOWNLOAD_FILE_PATH = '/tmp/'
logger = Logger.get_logger()


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


def refresh_instagram_token():
  logger.info('refresh instagram token.')
  settings = Settings.get_instance()
  insta = InstagramClient(settings.get_config('INSTAGRAM_ACCESS_TOKEN'))

  result, new_token = insta.refresh_token()
  if not result:
    logger.error('refresh instagram token fails.')
    return
  logger.info('new token:' + new_token)
  settings.set_config('INSTAGRAM_ACCESS_TOKEN', new_token)


def get_instagram_recent_post(interval):
  """get Instagram recent post"""

  settings = Settings.get_instance()
  insta = InstagramClient(settings.get_config('INSTAGRAM_ACCESS_TOKEN'))

  result, media = insta.get_recent_media()
  if not result:
    logger.error('get instagram recent post error.')
    return False, '', []

  created_time = media.get_timestamp()
  now_time = datetime.now(timezone.utc)
  delta = now_time - created_time

  if int(delta.total_seconds()) >= interval + 10:
    logger.info('no recent media.')
    return False, '', []

  caption = media.get_caption()
  urls = media.get_media_urls()

  logger.info('get instagram Caption: ' + caption)

  return True, caption, urls


def post_twitter(caption, paths):
  """post twitter"""

  logger.info("post twitter Caption: " + caption)

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
    logger.error('Network unreachable?')


def main_routine():
  """main routine"""
  settings = Settings.get_instance()
  interval = int(settings.get_config('INTERVAL_SECONDS'))

  schedule.every(interval).seconds.do(get_and_post, (interval))
  schedule.every().monday.do(refresh_instagram_token)

  logger.info('I2T INTERVAL:' + str(interval) + ' secs')
  while True:
    schedule.run_pending()
    time.sleep(1)


# main
if __name__ == '__main__':
  main_routine()
