#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy

class TwitterClient:

    def __init__(self, con_key, con_secret, token, token_secret):
        auth = tweepy.OAuthHandler(con_key, con_secret)
        auth.set_access_token(token, token_secret)

        self.api = tweepy.API(auth)


    def post(self, message):
        self.api.update_status(message)

    def postWithMedia(self, message, filepath):
        self.api.update_with_media(filepath, status=message)






