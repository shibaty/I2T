#!/usr/bin/env python
# -*- coding: utf-8 -*-

from instagram.client import InstagramAPI

class InstagramClient:

    def __init__(self, access_token, client_secret):
        self.api = InstagramAPI(
            access_token=access_token,
            client_secret=client_secret)

    def getRecentMedia(self):
        recent_media = self.api.user_recent_media(count=1)
        media = recent_media[0][0]

        return InstagramClientMedia(media)


class InstagramClientMedia:

    def __init__(self, media):
        self.media = media

    def getCaption(self):
        return self.media.caption.text

    def getImageUrl(self):
        return self.media.get_standard_resolution_url();

    def getCreatedTime(self):
        return self.media.created_time

    def getLink(self):
        return self.media.link
