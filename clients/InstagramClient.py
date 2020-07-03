# -*- coding: utf-8 -*-
"""Instagram Client for get recent media"""
from datetime import datetime
import requests


class InstagramGateway(object):

  def __init__(self, access_token):
    """Constructor"""
    self.access_token = access_token

  def call_api(self, endpoint, params):
    url = 'https://graph.instagram.com' + endpoint
    params['access_token'] = self.access_token
    response = requests.get(url, params)
    return response.status_code, response.json()


class InstagramClient(object):
  """Instagram Client"""

  def __init__(self, access_token):
    """Constructor"""
    self.gateway = InstagramGateway(access_token)

  def refresh_token(self):
    status, response_json = self.gateway.call_api(
        '/refresh_access_token', {'grant_type': 'ig_refresh_token'})
    if status != requests.codes.ok:
      return False, None
    new_access_token = response_json['access_token']
    self.gateway = InstagramGateway(new_access_token)
    return True, new_access_token

  def get_recent_media(self):
    """get recent media"""

    status, media_ids = self.gateway.call_api(
        '/me/media', {'fields': 'id'})
    if status != requests.codes.ok:
      return False, None
    recent_media_id = media_ids['data'][0]['id']
    status, media = self.gateway.call_api(
        '/' + str(recent_media_id), {'fields': 'id,caption,media_type,media_url,timestamp'})
    if status != requests.codes.ok:
      return False, None
    return True, InstagramClientMedia(self.gateway, media)


class InstagramClientMedia(object):
  """Instagram Client Media"""

  def __init__(self, gateway, media):
    """Constructor"""
    self.gateway = gateway
    self.media = media

  def get_caption(self):
    """get caption"""
    return self.media['caption']

  def get_media_urls(self):
    """get media urls"""
    urls = []
    if self.media['media_type'] == 'CAROUSEL_ALBUM':
      status, children_response = self.gateway.call_api(
          '/' + self.media['id'] + '/children', {'fields': 'media_url'})
      if status != requests.codes.ok:
        return None
      children = children_response['data']
      for child in children:
        urls.append(child['media_url'])
    else:
      urls.append(self.media['media_url'])
    return urls

  def get_timestamp(self):
    """get timestamp"""
    return datetime.strptime(self.media['timestamp'], "%Y-%m-%dT%H:%M:%S%z")
