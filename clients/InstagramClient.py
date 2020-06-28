# -*- coding: utf-8 -*-
"""Instagram Client for get recent media"""
from datetime import datetime
import requests


class InstagramClient(object):
  """Instagram Client"""

  def __init__(self, access_token):
    """Constructor"""
    self.access_token = access_token

  def get_recent_media(self):
    """get recent media"""

    recent_media_id = self.call_api(
        '/me/media', {'fields': 'id'})['data'][0]['id']
    media = self.call_api('/' + str(recent_media_id),
                          {'fields': 'id,caption,media_type,media_url,timestamp'})
    return InstagramClientMedia(self, media)

  def call_api(self, endpoint, params):
    url = 'https://graph.instagram.com' + endpoint
    params['access_token'] = self.access_token
    response = requests.get(url, params)
    return response.json()


class InstagramClientMedia(object):
  """Instagram Client Media"""

  def __init__(self, client, media):
    """Constructor"""
    self.client = client
    self.media = media

  def get_caption(self):
    """get caption"""
    return self.media['caption']

  def get_media_urls(self):
    """get media urls"""
    urls = []
    if self.media['media_type'] == 'CAROUSEL_ALBUM':
      children = self.client.call_api(
          '/' + self.media['id'] + '/children', {'fields': 'media_url'})['data']
      for child in children:
        urls.append(child['media_url'])
    else:
      urls.append(self.media['media_url'])
    return urls

  def get_timestamp(self):
    """get timestamp"""
    return datetime.strptime(self.media['timestamp'], "%Y-%m-%dT%H:%M:%S%z")
