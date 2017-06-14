#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instagram Client for get recent media"""

from instagram.client import InstagramAPI

class InstagramClient(object):
    """Instagram Client"""

    def __init__(self, access_token, client_secret):
        self.api = InstagramAPI(
            access_token=access_token, client_secret=client_secret)

    def get_recent_media(self):
        """get recent media"""
        recent_media = self.api.user_recent_media(count=1)
        media = recent_media[0][0]

        return InstagramClientMedia(media)


class InstagramClientMedia(object):
    """Instagram Client Media"""

    def __init__(self, media):
        """Constructor"""
        self.media = media

    def get_caption(self):
        """get caption"""
        return self.media.caption.text

    def get_image_url(self):
        """get image url"""
        return self.media.get_standard_resolution_url()

    def get_created_time(self):
        """get created time"""
        return self.media.created_time

    def get_link(self):
        """get link"""
        return self.media.link
