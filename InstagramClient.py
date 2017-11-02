#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instagram Client for get recent media"""

from datetime import datetime
import requests

# pylint: disable=R0903
class InstagramClient(object):
    """Instagram Client"""

    def __init__(self, access_token, client_secret):
        """Constructor"""
        self.access_token = access_token
        self.client_secret = client_secret

    def get_recent_media(self):
        """get recent media"""
        endpoint = "https://api.instagram.com/v1/users/self/media/recent"
        params = {'access_token': self.access_token, 'count': 1}

        response = requests.get(endpoint, params)

        return InstagramClientMedia(response.json()['data'][0])

class InstagramClientMedia(object):
    """Instagram Client Media"""

    def __init__(self, media):
        """Constructor"""
        self.media = media

    def get_caption(self):
        """get caption"""
        return self.media['caption']['text']

    def get_media_urls(self):
        """get media urls"""
        urls = []
        if self.media['type'] == 'carousel':
            for carousel in self.media['carousel_media']:
                urls.append(self.__get_standard_resolution_url(carousel))
        else:
            urls.append(self.__get_standard_resolution_url(self.media))
        return urls

    def get_created_time(self):
        """get created time"""
        return datetime.utcfromtimestamp(float(self.media['created_time']))

    def get_link(self):
        """get link"""
        return self.media['link']

    @classmethod
    def __get_standard_resolution_url(cls, obj):
        """get standard resolution media url"""
        if obj['type'] == 'image':
            url = obj['images']['standard_resolution']['url']
        else:
            url = obj['videos']['standard_resolution']['url']
        return url
