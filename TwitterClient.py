#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Twitter Client"""

import tweepy

class TwitterClient(object):
    """Twitter Client"""

    def __init__(self, con_key, con_secret, token, token_secret):
        auth = tweepy.OAuthHandler(con_key, con_secret)
        auth.set_access_token(token, token_secret)

        self.api = tweepy.API(auth)

    def post(self, message):
        """Post Message"""
        self.api.update_status(message)

    def post_with_media(self, message, filepath):
        """Post Message with Media"""
        self.api.update_with_media(filepath, status=message)
