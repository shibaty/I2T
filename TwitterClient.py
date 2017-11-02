#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Twitter Client"""

import twitter

class TwitterClient(object):
    """Twitter Client"""

    def __init__(self, con_key, con_secret, token, token_secret):
        """Constructor"""
        self.auth = twitter.OAuth(token, token_secret, con_key, con_secret)
        self.api = twitter.Twitter(auth=self.auth)
        self.upload_api = twitter.Twitter(domain="upload.twitter.com", auth=self.auth)

    def post(self, message):
        """Post Message"""
        self.api.statuses.update(status=message)

    def media_upload(self, path):
        """Media Upload"""
        with open(path, 'rb') as file:
            data = file.read()
            result = self.upload_api.media.upload(media=data)
        return result

    def post_with_medias(self, message, paths):
        """Post Message with Medias"""
        media_ids = []
        for path in paths:
            result = self.media_upload(path)
            media_ids.append(result['media_id_string'])
        self.api.statuses.update(
            media_ids=self.__list2csv(media_ids), status=message)

    @classmethod
    def __list2csv(cls, items):
        return ",".join(items)
