# -*- coding: utf-8 -*-
"""Twitter Client"""

import os.path
import time
import twitter


class TwitterClient(object):
  """Twitter Client"""

  def __init__(self, con_key, con_secret, token, token_secret):
    """Constructor"""
    self.auth = twitter.OAuth(token, token_secret, con_key, con_secret)
    self.api = twitter.Twitter(auth=self.auth)
    self.upload_api = twitter.Twitter(
        domain="upload.twitter.com", auth=self.auth)

  def post(self, message):
    """Post Message"""
    self.api.statuses.update(status=message)

  def media_upload(self, path, mime_type):
    """Media Upload"""
    file_size = os.path.getsize(path)
    media_category = 'TweetImage'
    if 'video' in mime_type:
      media_category = 'TweetVideo'
    media_id = self.upload_api.media.upload(
        command='INIT', media_type=mime_type,
        media_category=media_category,
        total_bytes=file_size)['media_id_string']

    with open(path, 'rb') as file:
      seg_id = 0
      bytes_sent = 0
      while bytes_sent < file_size:
        # Chunk size is less than 5M bytes
        chunk = file.read(4 * 1024 * 1024)
        self.upload_api.media.upload(
            command='APPEND',
            media_id=media_id,
            media=chunk,
            segment_index=seg_id)
        bytes_sent = file.tell()
        seg_id = seg_id + 1

    finalize_result = self.upload_api.media.upload(
        command='FINALIZE',
        media_id=media_id)

    if 'processing_info' in finalize_result:
      processing_info = finalize_result['processing_info']
      while processing_info['state'] != 'succeeded':
        if processing_info['state'] == 'failed':
          return ""

        time.sleep(processing_info['check_after_secs'])

        status_result = self.upload_api.media.upload(
            command='STATUS',
            media_id=media_id,
            _method='GET')
        if 'processing_info' not in status_result:
          break
        processing_info = status_result['processing_info']

    return media_id

  def post_with_medias(self, message, media_ids):
    """Post Message with Medias"""
    self.api.statuses.update(
        media_ids=self.__list2csv(media_ids), status=message)

  @classmethod
  def __list2csv(cls, items):
    return ",".join(items)
